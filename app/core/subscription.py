import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Subscription
from app.db.models.subscription import PlanType, SubscriptionStatus
from app.core.payments import plan_duration

logger = logging.getLogger(__name__)


async def get_active_subscription(db: AsyncSession, user_id: int) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == SubscriptionStatus.active)
        .order_by(Subscription.end_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def has_active_subscription(db: AsyncSession, user_id: int) -> bool:
    sub = await get_active_subscription(db, user_id)
    if not sub:
        return False
    return sub.end_date.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)


async def create_subscription_after_payment(
    db: AsyncSession,
    user_id: int,
    plan_type: str,
) -> Subscription:
    now = datetime.now(timezone.utc)
    duration = plan_duration(plan_type)
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == SubscriptionStatus.active)
        .with_for_update()
        .order_by(Subscription.end_date.desc())
        .limit(1)
    )
    current = result.scalar_one_or_none()
    if current and current.end_date.replace(tzinfo=timezone.utc) > now:
        start = current.end_date
        end = start + duration
        sub = Subscription(
            user_id=user_id,
            plan_type=PlanType(plan_type),
            start_date=start,
            end_date=end,
            status=SubscriptionStatus.active,
        )
    else:
        sub = Subscription(
            user_id=user_id,
            plan_type=PlanType(plan_type),
            start_date=now,
            end_date=now + duration,
            status=SubscriptionStatus.active,
        )
    db.add(sub)
    await db.flush()
    logger.info("Created subscription id=%s user_id=%s end_date=%s", sub.id, user_id, sub.end_date)
    return sub
