# app/api/v1/jotform_Webhook.py
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaSyncRoute
from fastapi import APIRouter, HTTPException

from app.api.models.Jotform.jotform_model import JotformWebhookPayload
from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.service.jotform_webhook_service import JotformWebhookService

jotform_public_router = APIRouter(
    prefix="/webhooks/jotform",
    tags=["jotform-webhooks-public"],
    route_class=DishkaSyncRoute,
)

@jotform_public_router.post("/{webhook_token}", status_code=201)
async def receive_jotform_submission(
        webhook_token: str,
        payload: JotformWebhookPayload,
        service: FromDishka[JotformWebhookService],
):
    try:
        appointment = service.process_submission(webhook_token=webhook_token, raw_request=payload.rawRequest)
    except JotformDomainError:
        raise HTTPException(status_code=404, detail="Invalid webhook token")

    return {
        "success": True,
        "appointment_id": appointment.id,
        "status": appointment.status,
    }