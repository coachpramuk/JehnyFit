from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню: 3 действия."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Купить абонемент", callback_data="start:buy"),
    )
    builder.row(
        InlineKeyboardButton(text="💪 Про тренировки", callback_data="start:trainings"),
    )
    builder.row(
        InlineKeyboardButton(
            text="🌸 Восстановление после родов",
            callback_data="start:recovery",
        ),
    )
    return builder.as_markup()


def subscription_plans_keyboard() -> InlineKeyboardMarkup:
    """Выбор тарифа: 3 плана + В меню."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1 месяц — $32", callback_data="plan:1m"),
    )
    builder.row(
        InlineKeyboardButton(text="8 недель — $60 · хит", callback_data="plan:8w"),
    )
    builder.row(
        InlineKeyboardButton(text="6 месяцев — $160", callback_data="plan:6m"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_main"),
    )
    return builder.as_markup()


def back_to_trainings_keyboard() -> InlineKeyboardMarkup:
    """⬅️ Назад в раздел тренировок."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_trainings"),
    )
    return builder.as_markup()


def back_to_plans_keyboard() -> InlineKeyboardMarkup:
    """⬅️ Назад к тарифам."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ К тарифам", callback_data="back_to_plans"),
    )
    return builder.as_markup()


def trainings_keyboard() -> InlineKeyboardMarkup:
    """Раздел «Узнать про тренировки»: 5 пунктов + Купить + В меню."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Тарифы", callback_data="trainings:price"),
    )
    builder.row(
        InlineKeyboardButton(text="📦 Что входит", callback_data="trainings:included"),
    )
    builder.row(
        InlineKeyboardButton(text="🎯 С чего начать", callback_data="trainings:beginner"),
    )
    builder.row(
        InlineKeyboardButton(text="👩‍🏫 О тренере", callback_data="trainings:trainer"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ FAQ", callback_data="trainings:faq"),
    )
    builder.row(
        InlineKeyboardButton(text="💳 Купить абонемент", callback_data="start:buy"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_main"),
    )
    return builder.as_markup()


def recovery_keyboard() -> InlineKeyboardMarkup:
    """Восстановление после родов: Купить курс + В меню."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Купить курс", callback_data="recovery:buy"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_main"),
    )
    return builder.as_markup()


