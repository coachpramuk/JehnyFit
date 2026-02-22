import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_bot: Optional[Bot] = None
_dp: Optional[Dispatcher] = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def get_storage() -> RedisStorage:
    from redis.asyncio import Redis
    return RedisStorage.from_url(settings.redis_url)


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        _dp = Dispatcher(storage=get_storage())
        from app.bot.handlers import user, admin
        from app.bot.middlewares.user_db import UserDbMiddleware
        from app.bot.middlewares.subscription import SubscriptionMiddleware
        _dp.message.middleware(UserDbMiddleware())
        _dp.callback_query.middleware(UserDbMiddleware())
        _dp.message.middleware(SubscriptionMiddleware())
        _dp.callback_query.middleware(SubscriptionMiddleware())
        _dp.include_router(user.router)
        _dp.include_router(admin.router)
    return _dp
