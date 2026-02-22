import logging
from app.tasks.celery_app import celery_app
from app.services.telegram_api import create_chat_invite_link, send_message
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, max_retries=3)
def send_subscription_invite(self, telegram_id: int) -> None:
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            link = loop.run_until_complete(
                create_chat_invite_link(settings.private_group_id, member_limit=1)
            )
            if link:
                loop.run_until_complete(
                    send_message(
                        telegram_id,
                        "<b>Оплата прошла успешно</b>\n\n"
                        "Ваша подписка активирована.\n\n"
                        f"Вступить в закрытую группу: {link}\n\n"
                        "Ссылка одноразовая.",
                    )
                )
                logger.info("Sent invite to %s", telegram_id)
            else:
                logger.warning("Could not create invite link for %s", telegram_id)
        finally:
            loop.close()
    except Exception as exc:
        logger.exception("send_subscription_invite failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)
