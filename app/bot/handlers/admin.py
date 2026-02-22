import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from app.bot.filters import IsAdmin, IsManager
from app.db.session import async_session_maker
from app.db.models import User, Subscription, Broadcast
from app.db.models.subscription import SubscriptionStatus
from sqlalchemy import select, func

router = Router()
logger = logging.getLogger(__name__)

admin_filter = IsAdmin()
manager_filter = IsManager()


@router.message(Command("stats"), admin_filter)
async def cmd_stats(message: Message) -> None:
    async with async_session_maker() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
        active_subs = (
            await session.execute(
                select(func.count(Subscription.id)).where(Subscription.status == SubscriptionStatus.active)
            )
        ).scalar() or 0
    await message.answer(
        f"📊 Статистика\n\n"
        f"Пользователей: {total_users}\n"
        f"Активных подписок: {active_subs}",
    )


@router.message(Command("users"), admin_filter)
async def cmd_users(message: Message) -> None:
    async with async_session_maker() as session:
        result = await session.execute(select(User).limit(50))
        users = result.scalars().all()
    lines = [f"{u.telegram_id} @{u.username or '—'} {u.first_name or ''}" for u in users]
    await message.answer("Пользователи (до 50):\n" + "\n".join(lines) or "Нет данных.")


@router.message(Command("subscriptions"), admin_filter)
async def cmd_subscriptions(message: Message) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.status == SubscriptionStatus.active).limit(50)
        )
        subs = result.scalars().all()
    lines = [f"user_id={s.user_id} plan={s.plan_type} end={s.end_date}" for s in subs]
    await message.answer("Активные подписки:\n" + "\n".join(lines) or "Нет данных.")


@router.message(Command("broadcast"), admin_filter)
async def cmd_broadcast(message: Message) -> None:
    await message.answer(
        "Рассылка. Ответьте на это сообщение текстом для рассылки всем пользователям. "
        "Или отправьте: /broadcast subscribers или /broadcast tag <tag>",
    )


@router.message(Command("add_tag"), manager_filter)
async def cmd_add_tag(message: Message) -> None:
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /add_tag <telegram_id> <tag>")
        return
    try:
        telegram_id = int(parts[1])
        tag = parts[2].strip()
    except ValueError:
        await message.answer("telegram_id должен быть числом.")
        return
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Пользователь не найден.")
            return
        if tag not in user.tags:
            user.tags = list(user.tags) + [tag]
            await session.commit()
        await message.answer(f"Тег {tag} добавлен пользователю {telegram_id}.")


@router.message(Command("remove_tag"), manager_filter)
async def cmd_remove_tag(message: Message) -> None:
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /remove_tag <telegram_id> <tag>")
        return
    try:
        telegram_id = int(parts[1])
        tag = parts[2].strip()
    except ValueError:
        await message.answer("telegram_id должен быть числом.")
        return
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Пользователь не найден.")
            return
        user.tags = [t for t in user.tags if t != tag]
        await session.commit()
        await message.answer(f"Тег {tag} удалён у пользователя {telegram_id}.")


@router.message(Command("run_scenario"), admin_filter)
async def cmd_run_scenario(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Использование: /run_scenario <scenario_id> <telegram_id>")
        return
    try:
        scenario_id = int(parts[1])
        telegram_id = int(parts[2])
    except ValueError:
        await message.answer("scenario_id и telegram_id должны быть числами.")
        return
    from app.db.models import Scenario
    from app.core.subscription import has_active_subscription
    from app.core.scenarios import get_first_step, send_step
    from app.bot.loader import get_bot
    async with async_session_maker() as session:
        result = await session.execute(select(Scenario).where(Scenario.id == scenario_id, Scenario.is_active == True))
        scenario = result.scalar_one_or_none()
        if not scenario:
            await message.answer("Сценарий не найден или неактивен.")
            return
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Пользователь не найден.")
            return
        if scenario.subscription_required and not await has_active_subscription(session, user.id):
            await message.answer("У пользователя нет активной подписки.")
            return
        steps = scenario.json_structure.get("steps", [])
        first = get_first_step(steps)
        if not first:
            await message.answer("В сценарии нет шагов.")
            return
        bot = get_bot()
        await send_step(bot, telegram_id, first)
        await message.answer(f"Сценарий «{scenario.name}» запущен для {telegram_id}, отправлен первый шаг.")


@router.message(Command("create_tariff"), admin_filter)
async def cmd_create_tariff(message: Message) -> None:
    await message.answer("Тарифы задаются в коде (PlanType). Для кастомных тарифов добавьте модель Tariff.")


@router.message(Command("update_tariff"), admin_filter)
async def cmd_update_tariff(message: Message) -> None:
    await message.answer("Обновление тарифов — см. модель и админку.")
