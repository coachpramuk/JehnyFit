import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command

from app.bot.keyboards import (
    back_to_plans_keyboard,
    back_to_trainings_keyboard,
    recovery_keyboard,
    start_menu_keyboard,
    subscription_plans_keyboard,
    trainings_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)

# Все сообщения: parse_mode=HTML, единый стиль — заголовок, отступы, списки
START_MESSAGE = (
    "👋 <b>Привет! Я бот Jenny Fit</b>\n\n"
    "Клуб домашних тренировок: абонементы, программы и поддержка тренера.\n\n"
    "Выбери кнопку ниже 👇\n"
    "Вопросы — в службу заботы 💬"
)

BUY_SUBSCRIPTION_MESSAGE = (
    "💳 <b>Выбери абонемент</b>\n\n"
    "· <b>1 месяц</b> — $32\n"
    "· <b>8 недель</b> — $60\n"
    "· <b>6 месяцев</b> — $160\n\n"
    "Проблемы с оплатой? Меню → Помощь 💬"
)

TRAININGS_MESSAGE = (
    "💪 <b>Про тренировки</b>\n\n"
    "Программы и библиотека 500+ тренировок.\n\n"
    "· Экономия — как 2–3 занятия в зале\n"
    "· Комфорт — в своё время\n"
    "· Каждый день готовая тренировка\n\n"
    "Выбери пункт ниже 👇"
)

RECOVERY_MESSAGE = (
    "🌸 <b>Восстановление после родов и плоский живот</b>\n\n"
    "40 уроков от простого к сложному. Тело изнутри.\n\n"
    "<b>Для кого</b>\n"
    "· Мамы после родов\n"
    "· Диастаз, тазовое дно\n\n"
    "<b>Структура</b>\n"
    "· Базовый блок — дыхание, тазовое дно\n"
    "· Интеграция — глубокие мышцы + движение\n"
    "· Сила и функциональность\n\n"
    "<b>Результат</b>\n"
    "· Подтянутый живот, осанка, понимание как сохранить"
)

PRICE_ABONEMENT_MESSAGE = (
    "💰 <b>Сколько стоит абонемент</b>\n\n"
    "<b>Базовый</b> — 1 месяц, $32\n"
    "· Программа + библиотека 300+\n"
    "· Для знакомства с клубом\n\n"
    "<b>Optima</b> (хит) — 8 недель, $60\n"
    "· Всё из Базового + поддержка в чате\n\n"
    "<b>Премиум</b> — 6 месяцев, $160\n"
    "· Всё из Optima + приоритет + консультация\n"
    "· 26$/мес (экономия 36%)"
)

INCLUDED_MESSAGE = (
    "✅ <b>Что входит</b>\n\n"
    "· Доступ к текущей программе\n"
    "· Библиотека 300+ тренировок:\n"
    "  восстановление, лицо, силовые, пилатес, растяжка, стопы, пресс\n\n"
    "<b>Длительность</b>\n"
    "· Основные силовые — <b>~30 мин</b>\n"
    "· Доп. оздоровительные — <b>10–15 мин</b>\n\n"
    "· Ежедневные обновления\n"
    "· Поддержка тренера\n\n"
    "Можно идти по программе или выбирать из библиотеки."
)

BEGINNER_MESSAGE = (
    "🎯 <b>С чего начать</b>\n\n"
    "<b>Шаг 1.</b> Нажми «Купить абонемент» и выбери тариф.\n\n"
    "<b>Шаг 2.</b> После оплаты тренировки появятся в Telegram.\n"
    "«Тренировка на сегодня» → плей → занимаешься.\n\n"
    "<b>Как заниматься</b>\n"
    "По программе по шагам или любые тренировки из библиотеки (раздел «Что входит»).\n\n"
    "Новичкам — <b>Лайт фит</b>. При регулярности — прогресс 💪"
)

TRAINER_MESSAGE = (
    "👩‍🏫 <b>О тренере</b>\n\n"
    "<b>Евгения Сасковец (Jenny Fit)</b>\n\n"
    "· 10 лет в фитнесе\n"
    "· Мама троих детей\n"
    "· 100+ человек в клубе\n"
    "· 500+ довольных клиентов\n\n"
    "Безопасные упражнения, результат с простым оборудованием."
)

FAQ_MESSAGE = (
    "💬 <b>Частые вопросы</b>\n\n"
    "<b>Доступ не с начала программы?</b>\n"
    "Доступ ко всем тренировкам. Срок по тарифу: 30 дней, 8 нед. или 6 мес.\n\n"
    "<b>Время выхода тренировок?</b>\n"
    "Пн–Сб 6:00 МСК. Заниматься можно в любое время, тренировки не исчезают.\n\n"
    "<b>Новичок, боюсь силовых?</b>\n"
    "Курс «Лайт фит» — 4 недели, мягкий вход. Потом легко к основным программам.\n\n"
    "<b>Восстановление после родов?</b>\n"
    "Да. «Всё включено» и другие — в разделе «Восстановление после родов».\n\n"
    "<b>Заморозка?</b>\n"
    "7 дней один раз в месяц.\n\n"
    "<b>Когда результат?</b>\n"
    "При регулярности — первые ощущения и прогресс. Зависит от регулярности и питания."
)

# Путь к фото с тарифами и к фото тренера (static/ в корне проекта)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # app/bot/handlers -> project root
PRICE_PHOTO_PATH = PROJECT_ROOT / "static" / "price_plans.png"
TRAINER_PHOTO_PATH = PROJECT_ROOT / "static" / "trainer.png"


@router.message(CommandStart())
async def cmd_start(message: Message, has_subscription: bool) -> None:
    await message.answer(
        START_MESSAGE,
        reply_markup=start_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "💬 <b>Помощь</b>\n\n"
        "Вопросы по абонементу, оплате или тренировкам — напиши сюда, ответим.",
    )


# Обработчики выбора кнопок под сообщением (inline)
@router.callback_query(F.data == "start:buy")
async def btn_buy_subscription(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        BUY_SUBSCRIPTION_MESSAGE,
        reply_markup=subscription_plans_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "start:trainings")
async def btn_trainings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        TRAININGS_MESSAGE,
        reply_markup=trainings_keyboard(),
    )
    await callback.answer()


# Сколько стоит абонемент — текст + фото
@router.callback_query(F.data == "trainings:price")
async def trainings_price(callback: CallbackQuery) -> None:
    await callback.answer()
    back_kb = back_to_trainings_keyboard()
    if PRICE_PHOTO_PATH.is_file():
        photo = FSInputFile(PRICE_PHOTO_PATH)
        await callback.message.answer_photo(
            photo=photo,
            caption=PRICE_ABONEMENT_MESSAGE,
            reply_markup=back_kb,
        )
    else:
        await callback.message.answer(
            PRICE_ABONEMENT_MESSAGE,
            reply_markup=back_kb,
        )


@router.callback_query(F.data == "trainings:included")
async def trainings_included(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        INCLUDED_MESSAGE,
        reply_markup=back_to_trainings_keyboard(),
    )


@router.callback_query(F.data == "trainings:beginner")
async def trainings_beginner(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        BEGINNER_MESSAGE,
        reply_markup=back_to_trainings_keyboard(),
    )


@router.callback_query(F.data == "trainings:trainer")
async def trainings_trainer(callback: CallbackQuery) -> None:
    await callback.answer()
    back_kb = back_to_trainings_keyboard()
    if TRAINER_PHOTO_PATH.is_file():
        photo = FSInputFile(TRAINER_PHOTO_PATH)
        await callback.message.answer_photo(
            photo=photo,
            caption=TRAINER_MESSAGE,
            reply_markup=back_kb,
        )
    else:
        await callback.message.answer(
            TRAINER_MESSAGE,
            reply_markup=back_kb,
        )


@router.callback_query(F.data == "trainings:faq")
async def trainings_faq(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        FAQ_MESSAGE,
        reply_markup=back_to_trainings_keyboard(),
    )


@router.callback_query(F.data == "start:recovery")
async def btn_recovery(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        RECOVERY_MESSAGE,
        reply_markup=recovery_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "recovery:buy")
async def recovery_buy(callback: CallbackQuery) -> None:
    """Купить курс восстановления — переход к выбору абонемента."""
    await callback.message.edit_text(
        BUY_SUBSCRIPTION_MESSAGE,
        reply_markup=subscription_plans_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "start:glutes")
async def _redirect_glutes_to_included(callback: CallbackQuery) -> None:
    """Редирект устаревшего callback в «Что входит»."""
    await callback.message.edit_text(
        INCLUDED_MESSAGE,
        reply_markup=back_to_trainings_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "back_trainings")
async def back_trainings(callback: CallbackQuery) -> None:
    """Возврат в раздел «Узнать про тренировки»."""
    await callback.answer()
    # Сообщение с фото нельзя заменить на текст — отправляем меню новым сообщением
    try:
        await callback.message.edit_text(
            TRAININGS_MESSAGE,
            reply_markup=trainings_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            TRAININGS_MESSAGE,
            reply_markup=trainings_keyboard(),
        )


@router.callback_query(F.data == "back_to_plans")
async def back_to_plans(callback: CallbackQuery) -> None:
    """Возврат к выбору тарифов."""
    await callback.message.edit_text(
        BUY_SUBSCRIPTION_MESSAGE,
        reply_markup=subscription_plans_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        START_MESSAGE,
        reply_markup=start_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "profile")
async def profile(
    callback: CallbackQuery,
    has_subscription: bool,
    db_user=None,
) -> None:
    if not db_user:
        await callback.answer("Ошибка")
        return
    status = "Активна" if has_subscription else "Нет активной подписки"
    await callback.message.edit_text(
        "👤 <b>Профиль</b>\n\n"
        f"Подписка: {status}\n"
        f"Username: @{db_user.username or '—'}",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("plan:"))
async def plan_selected(callback: CallbackQuery) -> None:
    plan = callback.data.split(":")[-1]
    # In production: create payment link and send to user
    await callback.message.edit_text(
        f"💳 <b>Тариф {plan}</b>\n\n"
        "Для оплаты перейди по ссылке (настрой платёжную систему в .env).",
        reply_markup=back_to_plans_keyboard(),
    )
    await callback.answer()
