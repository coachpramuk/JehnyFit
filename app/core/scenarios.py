"""
Scenario engine: executes JSON scenario steps (text, media, buttons, delayed steps, subscription check).
"""
import logging
from typing import Any, Optional

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)


def build_keyboard(buttons: list[dict]) -> Optional[InlineKeyboardMarkup]:
    if not buttons:
        return None
    builder = InlineKeyboardBuilder()
    for btn in buttons:
        builder.row(
            InlineKeyboardButton(
                text=btn.get("text", ""),
                callback_data=btn.get("callback_data", ""),
                url=btn.get("url"),
            )
        )
    return builder.as_markup()


async def send_step(bot: Bot, chat_id: int, step: dict) -> bool:
    step_type = step.get("type", "text")
    text = step.get("text", "")
    keyboard = build_keyboard(step.get("buttons", []))

    parse_mode = ParseMode.HTML
    if step_type == "image" and step.get("photo"):
        await bot.send_photo(
            chat_id, step["photo"],
            caption=text or None,
            reply_markup=keyboard,
            parse_mode=parse_mode,
        )
    elif step_type == "video" and step.get("video"):
        await bot.send_video(
            chat_id, step["video"],
            caption=text or None,
            reply_markup=keyboard,
            parse_mode=parse_mode,
        )
    elif step_type == "audio" and step.get("audio"):
        await bot.send_audio(
            chat_id, step["audio"],
            caption=text or None,
            reply_markup=keyboard,
            parse_mode=parse_mode,
        )
    elif step_type == "file" and step.get("file"):
        await bot.send_document(
            chat_id, step["file"],
            caption=text or None,
            reply_markup=keyboard,
            parse_mode=parse_mode,
        )
    else:
        await bot.send_message(
            chat_id,
            text or "(пусто)",
            reply_markup=keyboard,
            parse_mode=parse_mode,
        )
    return True


def get_next_step(steps: list[dict], step_id: str, button_callback: Optional[str] = None) -> Optional[dict]:
    step_map = {s["id"]: s for s in steps if s.get("id")}
    current = step_map.get(step_id)
    if not current:
        return None
    if button_callback:
        transitions = current.get("transitions", [])
        for t in transitions:
            if t.get("on_callback") == button_callback:
                return step_map.get(t["next_step_id"])
    return step_map.get(current.get("next_step_id", ""))


def get_first_step(steps: list[dict]) -> Optional[dict]:
    if not steps:
        return None
    first_id = steps[0].get("id")
    if first_id:
        return next((s for s in steps if s.get("id") == first_id), steps[0])
    return steps[0]
