import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import APIRouter, Request, Response, Header, HTTPException

from app.config import get_settings

router = APIRouter(prefix="/webhook", tags=["telegram"])
logger = logging.getLogger(__name__)
settings = get_settings()


def get_bot() -> Bot:
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_dp() -> Dispatcher:
    from app.bot.loader import get_dispatcher
    return get_dispatcher()


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    response: Response,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> dict[str, Any]:
    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        logger.warning("Invalid Telegram webhook secret")
        raise HTTPException(status_code=403, detail="Invalid secret")
    body = await request.json()
    update = Update.model_validate(body)
    dp = get_dp()
    bot = get_bot()
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}
