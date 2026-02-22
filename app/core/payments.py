import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.config import get_settings
from app.db.models import User, Payment, Subscription
from app.db.models.payment import PaymentStatus
from app.db.models.subscription import PlanType, SubscriptionStatus

logger = logging.getLogger(__name__)
settings = get_settings()

IDEMPOTENCY_TTL = 86400  # 24 hours


@dataclass
class PaymentWebhookPayload:
    provider: str
    external_id: str
    status: str
    amount: Optional[Decimal] = None
    currency: str = "RUB"
    user_telegram_id: Optional[int] = None


async def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def idempotency_check(provider: str, external_id: str) -> bool:
    redis = await get_redis()
    key = f"payment:idempotency:{provider}:{external_id}"
    try:
        added = await redis.set(key, "1", nx=True, ex=IDEMPOTENCY_TTL)
        return not added
    finally:
        await redis.aclose()


async def process_payment_webhook(db: AsyncSession, payload: PaymentWebhookPayload) -> Optional[int]:
    if payload.status not in ("succeeded", "completed", "paid", "success"):
        redis = await get_redis()
        try:
            await redis.set(
                f"payment:idempotency:{payload.provider}:{payload.external_id}",
                "1", ex=IDEMPOTENCY_TTL,
            )
        finally:
            await redis.aclose()
        logger.info("Payment %s status %s - not success, skipping subscription", payload.external_id, payload.status)
        return None

    result = await db.execute(select(Payment).where(Payment.external_id == payload.external_id))
    existing = result.scalar_one_or_none()
    if existing:
        if existing.status == PaymentStatus.completed:
            logger.info("Payment %s already completed, skip", payload.external_id)
            return None
        existing.status = PaymentStatus.completed
        await db.flush()
        user_id = existing.user_id
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        await activate_subscription_for_payment(db, user.id, payload)
        logger.info("Payment %s processed (existing), subscription activated", payload.external_id)
        return user.telegram_id
    else:
        if not payload.user_telegram_id:
            logger.error("Payment %s: no user_telegram_id", payload.external_id)
            return None
        result = await db.execute(select(User).where(User.telegram_id == payload.user_telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.error("Payment %s: user telegram_id=%s not found", payload.external_id, payload.user_telegram_id)
            return None
        payment = Payment(
            user_id=user.id,
            provider=payload.provider,
            external_id=payload.external_id,
            amount=payload.amount or Decimal("0"),
            currency=payload.currency,
            status=PaymentStatus.completed,
        )
        db.add(payment)
        await db.flush()
        await activate_subscription_for_payment(db, user.id, payload)
        logger.info("Payment %s processed, subscription activated", payload.external_id)
        return user.telegram_id

    return None


def plan_duration(plan_type: str) -> timedelta:
    if plan_type == PlanType.one_month.value:
        return timedelta(days=30)
    if plan_type == PlanType.eight_weeks.value:
        return timedelta(weeks=8)
    if plan_type == PlanType.six_months.value:
        return timedelta(days=180)
    return timedelta(days=30)


async def activate_subscription_for_payment(db: AsyncSession, user_id: int, payload: PaymentWebhookPayload) -> None:
    from app.core.subscription import create_subscription_after_payment
    plan = infer_plan_from_amount(payload.amount)
    await create_subscription_after_payment(db, user_id, plan)


def infer_plan_from_amount(amount: Optional[Decimal]) -> str:
    if amount is None:
        return PlanType.one_month.value
    a = float(amount)
    if a >= 1500:
        return PlanType.six_months.value
    if a >= 800:
        return PlanType.eight_weeks.value
    return PlanType.one_month.value
