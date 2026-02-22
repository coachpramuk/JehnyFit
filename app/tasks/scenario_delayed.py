"""
Delayed scenario step: run after N hours/days.
"""
import asyncio
import logging

from app.tasks.celery_app import celery_app
from app.core.scenarios import send_step
from app.bot.loader import get_bot

logger = logging.getLogger(__name__)


@celery_app.task
def run_delayed_scenario_step(telegram_id: int, step: dict) -> None:
    async def _run():
        bot = get_bot()
        await send_step(bot, telegram_id, step)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()
