from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.config import get_settings
from app.db.session import async_session_maker
from app.db.models import User
from app.db.models.user import UserRole
from sqlalchemy import select

settings = get_settings()


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        if not user:
            return False
        return user.id in settings.admin_ids_list


class IsManager(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        if not user:
            return False
        if user.id in settings.admin_ids_list:
            return True
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.telegram_id == user.id))
            u = result.scalar_one_or_none()
            return u is not None and u.role in (UserRole.manager, UserRole.admin)
