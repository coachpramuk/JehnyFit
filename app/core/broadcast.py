import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Broadcast
from app.db.models.subscription import SubscriptionStatus
from app.db.models.broadcast import BroadcastSegment, BroadcastStatus
from app.db.models import Subscription

logger = logging.getLogger(__name__)


async def get_recipients(
    db: AsyncSession,
    segment: BroadcastSegment,
    tag: Optional[str] = None,
) -> list[int]:
    if segment == BroadcastSegment.all:
        result = await db.execute(select(User.telegram_id))
        return list(result.scalars().all())
    if segment == BroadcastSegment.subscribers:
        result = await db.execute(
            select(User.telegram_id).join(Subscription).where(
                Subscription.status == SubscriptionStatus.active,
                Subscription.end_date > datetime.now(timezone.utc),
            ).distinct()
        )
        return list(result.scalars().all())
    if segment == BroadcastSegment.tag and tag:
        result = await db.execute(
            select(User.telegram_id).where(User.tags.contains([tag]))
        )
        return list(result.scalars().all())
    return []
