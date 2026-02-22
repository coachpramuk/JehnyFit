import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.db.session import async_session_maker
from app.db.models import User, Subscription
from app.db.models.subscription import SubscriptionStatus
from app.services.telegram_api import kick_chat_member, send_message
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _expire_subscriptions_impl() -> None:
    now = datetime.now(timezone.utc)
    async with async_session_maker() as db:
        result = await db.execute(
            select(Subscription)
            .where(Subscription.status == SubscriptionStatus.active, Subscription.end_date <= now)
        )
        subs = result.scalars().all()
        for sub in subs:
            sub.status = SubscriptionStatus.expired
            user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one()
            await kick_chat_member(settings.private_group_id, user.telegram_id)
            await send_message(
                user.telegram_id,
                "Ваша подписка истекла. Спасибо, что были с нами! Продлить подписку можно в боте.",
            )
            logger.info("Expired subscription id=%s user_id=%s", sub.id, sub.user_id)
        await db.commit()


@celery_app.task
def expire_subscriptions() -> None:
    _run_async(_expire_subscriptions_impl())
