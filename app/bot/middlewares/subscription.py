from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.subscription import has_active_subscription
from app.bot.middlewares.user_db import get_user_from_context, CONTEXT_SESSION_KEY


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = await get_user_from_context(event)
        session = data.get(CONTEXT_SESSION_KEY)
        data["has_subscription"] = False
        if user and session:
            data["has_subscription"] = await has_active_subscription(session, user.id)
        return await handler(event, data)
