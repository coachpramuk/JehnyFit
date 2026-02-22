import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import get_settings
from api.routes import health, webhook_telegram, webhook_payment

logging.basicConfig(
    level=get_settings().log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Описание бота — только plain text (Telegram не поддерживает HTML в description/about)
BOT_SHORT_DESCRIPTION = "Клуб домашних тренировок Jenny Fit. Абонементы, программы, поддержка тренера."
BOT_DESCRIPTION = (
    "Клуб домашних тренировок Jenny Fit. Узнай о программах, купи абонемент и тренируйся дома. "
    "Доступ к библиотеке тренировок, восстановление после родов, программы для новичков. "
    "Оплата в боте, поддержка тренера."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from aiogram import Bot
        from aiogram.types import BotCommand, MenuButtonCommands
        settings = get_settings()
        if settings.telegram_bot_token:
            bot = Bot(token=settings.telegram_bot_token)
            await bot.set_my_commands([
                BotCommand(command="start", description="🍌 Начать — приветствие и меню"),
                BotCommand(command="help", description="Помощь / Служба заботы"),
            ])
            await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
            # Описание и «О боте» — без HTML (Telegram их не поддерживает)
            await bot.set_my_short_description(short_description=BOT_SHORT_DESCRIPTION)
            await bot.set_my_description(description=BOT_DESCRIPTION)
            await bot.session.close()
            logger.info("Bot menu and description set.")
    except Exception as e:
        logger.warning("Could not set bot menu/description: %s", e)
    yield
    logger.info("Shutdown complete.")


app = FastAPI(title="Telegram Subscription Bot", lifespan=lifespan)

app.include_router(health.router)
app.include_router(webhook_telegram.router)
app.include_router(webhook_payment.router)


@app.get("/")
async def root():
    return {"service": "telegram-subscription-bot", "docs": "/docs"}
