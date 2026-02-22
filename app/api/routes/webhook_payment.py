import logging
from typing import Any

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.payments import process_payment_webhook, idempotency_check, PaymentWebhookPayload
from app.config import get_settings

router = APIRouter(prefix="/webhook", tags=["payment"])
logger = logging.getLogger(__name__)
settings = get_settings()


def verify_payment_signature(body: bytes, signature: str | None) -> bool:
    if not settings.payment_webhook_secret:
        return True
    if not signature:
        return False
    import hmac
    import hashlib
    expected = hmac.new(
        settings.payment_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post("/payment")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_webhook_signature: str | None = None,
) -> dict[str, Any]:
    body = await request.body()
    if not verify_payment_signature(body, request.headers.get("X-Webhook-Signature") or x_webhook_signature):
        logger.warning("Invalid payment webhook signature")
        raise HTTPException(status_code=403, detail="Invalid signature")
    data = await request.json()
    payload = PaymentWebhookPayload(
        provider=settings.payment_provider,
        external_id=data.get("id") or data.get("payment_id") or str(data.get("external_id", "")),
        status=data.get("status", "").lower(),
        amount=data.get("amount"),
        currency=data.get("currency", "RUB"),
        user_telegram_id=data.get("user_telegram_id") or data.get("metadata", {}).get("telegram_id"),
    )
    if not payload.external_id or not payload.status:
        raise HTTPException(status_code=400, detail="Missing id or status")
    if await idempotency_check(payload.provider, payload.external_id):
        logger.info("Payment webhook idempotent skip: %s", payload.external_id)
        return {"ok": True, "processed": False}
    try:
        telegram_id = await process_payment_webhook(db, payload)
        if telegram_id is not None:
            from app.tasks.after_payment import send_subscription_invite
            send_subscription_invite.delay(telegram_id)
        return {"ok": True, "processed": True}
    except Exception as e:
        logger.exception("Payment webhook processing failed: %s", e)
        raise HTTPException(status_code=500, detail="Processing failed")
