from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db.session import get_session
from app.models.jotform_model import JotformProcessingResult
from app.repositories import appointment_repositories
from app.repositories.appointment_repositories import AppointmentRepository
from app.services import jotform_service

jotform_router = APIRouter(
    prefix="/webhooks/jotform",
    tags=["jotform-webhooks"]
)

@jotform_router.post("/webhook/{webhook_token}", status_code=201, response_model=JotformProcessingResult)
async def receive_jotform_webhook(
        webhook_token: str,
        request: Request,
        session: Session = Depends(get_session),
):
    """Receive Jotform webhook submission for a specific photographer
    Each photographer gets a unique webhook URL:
    POST /webhooks/jotform/123"""

    try:
        if not jotform_service.JotformService.validate_photographer(session, webhook_token):
            raise HTTPException(status_code=404, detail="Photographer not found")

        form_data = await request.form()
        form_dict = dict(form_data)

        if 'rawRequest' not in form_dict or not form_dict['rawRequest']:
            return {"error": "rawRequest field is missing or empty"}

        appointment_repository = AppointmentRepository(session)

        appointment = jotform_service.JotformService.process_webhook(repository= appointment_repository, payload= form_dict, photographer_id= photographer_id)

        return JotformProcessingResult(
            success=True,
            appointment_id=appointment.id,
            submission_id="0",
            photographer_id=str(photographer_id),
        )
    except HTTPException as err:
        raise err
    except Exception as e:
        print(f" Jotform webhook error: {str(e)} ")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")
