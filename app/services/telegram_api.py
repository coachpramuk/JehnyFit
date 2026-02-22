import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BASE_URL = "https://api.telegram.org/bot{token}"


async def create_chat_invite_link(chat_id: int, member_limit: int = 1) -> Optional[str]:
    url = BASE_URL.format(token=settings.telegram_bot_token) + "/createChatInviteLink"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                url,
                json={"chat_id": chat_id, "member_limit": member_limit},
                timeout=10.0,
            )
            data = r.json()
            if not data.get("ok"):
                logger.warning("createChatInviteLink failed: %s", data)
                return None
            return data.get("result", {}).get("invite_link")
        except Exception as e:
            logger.exception("createChatInviteLink error: %s", e)
            return None


async def revoke_chat_invite_link(chat_id: int, invite_link: str) -> bool:
    url = BASE_URL.format(token=settings.telegram_bot_token) + "/revokeChatInviteLink"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json={"chat_id": chat_id, "invite_link": invite_link}, timeout=10.0)
            return r.json().get("ok", False)
        except Exception as e:
            logger.exception("revokeChatInviteLink error: %s", e)
            return False


async def kick_chat_member(chat_id: int, user_id: int) -> bool:
    url = BASE_URL.format(token=settings.telegram_bot_token) + "/banChatMember"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json={"chat_id": chat_id, "user_id": user_id}, timeout=10.0)
            data = r.json()
            if not data.get("ok"):
                logger.warning("kick_chat_member failed: %s", data)
                return False
            return True
        except Exception as e:
            logger.exception("kick_chat_member error: %s", e)
            return False


async def unban_chat_member(chat_id: int, user_id: int) -> bool:
    url = BASE_URL.format(token=settings.telegram_bot_token) + "/unbanChatMember"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json={"chat_id": chat_id, "user_id": user_id}, timeout=10.0)
            return r.json().get("ok", False)
        except Exception as e:
            logger.exception("unban_chat_member error: %s", e)
            return False


async def send_message(chat_id: int, text: str) -> bool:
    url = BASE_URL.format(token=settings.telegram_bot_token) + "/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=10.0,
            )
            return r.json().get("ok", False)
        except Exception as e:
            logger.exception("send_message error: %s", e)
            return False
