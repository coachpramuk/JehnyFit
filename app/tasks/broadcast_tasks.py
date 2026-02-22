import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.db.session import async_session_maker
from app.db.models import Broadcast
from app.db.models.broadcast import BroadcastStatus
from app.core.broadcast import get_recipients
from app.services.telegram_api import send_message

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _send_broadcast_impl(broadcast_id: int) -> dict:
    async with async_session_maker() as db:
        result = await db.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
        broadcast = result.scalar_one_or_none()
        if not broadcast or broadcast.status != BroadcastStatus.draft:
            return {"ok": False, "reason": "not_found_or_not_draft"}
        broadcast.status = BroadcastStatus.sending
        await db.commit()

    from app.db.models.broadcast import BroadcastSegment
    async with async_session_maker() as db:
        recipients = await get_recipients(db, broadcast.segment, broadcast.segment_tag)
        content = broadcast.content
        text = content.get("text", "")
        sent = 0
        failed = 0
        for telegram_id in recipients:
            try:
                ok = await send_message(telegram_id, text)
                if ok:
                    sent += 1
                else:
                    failed += 1
            except Exception as e:
                logger.warning("Broadcast send failed %s: %s", telegram_id, e)
                failed += 1

    async with async_session_maker() as db:
        result = await db.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
        broadcast = result.scalar_one()
        broadcast.status = BroadcastStatus.completed
        broadcast.stats = {"total": len(recipients), "sent": sent, "failed": failed}
        broadcast.completed_at = datetime.now(timezone.utc)
        await db.commit()
    return {"sent": sent, "failed": failed, "total": len(recipients)}


@celery_app.task
def run_broadcast(broadcast_id: int) -> dict:
    return _run_async(_send_broadcast_impl(broadcast_id))
