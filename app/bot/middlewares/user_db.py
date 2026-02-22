import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.db.models import User
from app.db.models.user import UserRole

logger = logging.getLogger(__name__)

CONTEXT_USER_KEY = "db_user"
CONTEXT_SESSION_KEY = "db_session"


async def get_user_from_context(event: TelegramObject) -> User | None:
    data = event.model_extra or {}
    if isinstance(event, (Message, CallbackQuery)):
        data = getattr(event, "middleware_data", {}) or {}
    return data.get(CONTEXT_USER_KEY)


class UserDbMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
        if not user_id:
            return await handler(event, data)

        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                from app.db.models.user import UserStatus
                user = User(
                    telegram_id=user_id,
                    username=event.from_user.username if event.from_user else None,
                    first_name=event.from_user.first_name if event.from_user else None,
                    last_name=event.from_user.last_name if event.from_user else None,
                    role=UserRole.user,
                    status=UserStatus.active,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info("Created user telegram_id=%s", user_id)
            data[CONTEXT_USER_KEY] = user
            data[CONTEXT_SESSION_KEY] = session
            return await handler(event, data)
