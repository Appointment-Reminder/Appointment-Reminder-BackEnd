from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.api.models.Jotform.jotform_model import JotformCredentialRead, JotformCredentialCreate, \
    JotformCredentialUpdate, JotformFormCreate, JotformFormRead, JotformFormUpdate
from app.domain.user.models.user import User
from app.domain.Jotform.service.jotform_service import JotformService

jotform_router = APIRouter(
    prefix="/webhooks/jotform",
    tags=["jotform-webhooks"],
    route_class=DishkaRoute
)

"""
@jotform_router.post("/webhook/{webhook_token}", status_code=201, response_model=JotformProcessingResult)
async def receive_jotform_webhook(
        webhook_token: str,
        request: Request,
        session: Session = Depends(get_session),
):
    Receive Jotform webhook submission for a specific photographer
    Each photographer gets a unique webhook URL:
    POST /webhooks/jotform/123

    try:
        if not jotform_service.JotformWebhookProcessing.validate_photographer(session, webhook_token):
            raise HTTPException(status_code=404, detail="Photographer not found")

        form_data = await request.form()
        form_dict = dict(form_data)

        if 'rawRequest' not in form_dict or not form_dict['rawRequest']:
            return {"error": "rawRequest field is missing or empty"}

        appointment_repository = AppointmentRepository(session)

        appointment = jotform_service.JotformWebhookProcessing.process_webhook(repository= appointment_repository, payload= form_dict, business_member_token=webhook_token)

        return JotformProcessingResult(
            success=True,
            appointment_id=appointment.id,
            submission_id="0",
            photographer_id=appointment.user_id,
        )
    except HTTPException as err:
        raise err
    except Exception as e:
        print(f" Jotform webhook error: {str(e)} ")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")
"""

##CREDENTIALS
@jotform_router.post("/jotform/credentials", status_code=201, response_model=JotformCredentialRead)
async def create_jotform_credentials(
        credential: JotformCredentialCreate,
        service: FromDishka[JotformService],
        current_user: FromDishka[User]):
    return service.create_jotform_credential(credential, current_user)

@jotform_router.get("/business/{business_id}/jotform/credentials", status_code=200, response_model= List[JotformCredentialRead])
async def get_jotform_credentials(business_id: str, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.get_jotform_credentials(business_id, current_user)

@jotform_router.patch("/jotform/credentials", response_model=JotformCredentialRead)
async def update_jotform_credentials(credential: JotformCredentialUpdate, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.update_jotform_credentials(credential, current_user)

@jotform_router.delete("/jotform/credentials/{credential_id}")
async def delete_jotform_credentials(credential_id: str, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.delete_jotform_credentials(credential_id, current_user)

#FORM
@jotform_router.post("/jotform/form", status_code=201, response_model=JotformFormCreate)
async def jotform_form_create(form_data: JotformFormCreate, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.jotform_form_create(form_data, current_user)

@jotform_router.get("/jotform/form/{form_id}", status_code=200, response_model=JotformFormRead)
async def jotform_form_read(form_id: str, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.get_jotform_form_by_id(form_id, current_user)

@jotform_router.get("/business/{business_id}/jotform/form",response_model=List[JotformFormRead])
async def get_jotform_forms_for_business(business_id: str, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.get_jotform_form_by_business_id(business_id, current_user)

@jotform_router.get("/jotform/form/{member_id}/{category_id}", response_model=JotformFormRead)
async def get_jotform_forms_for_member_and_category(business_id: int, member_id: int, category_id: int, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.get_jotform_form_by_member_and_category(business_id=business_id,member_id=member_id, category_id=category_id, current_user=current_user)

@jotform_router.patch("/jotform/form", status_code=200, response_model=JotformFormRead)
async def jotform_form_update(form_data: JotformFormUpdate, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.update_jotform_form(form_data, current_user)

@jotform_router.delete("/jotform/form/{form_id}")
async def jotform_form_delete(form_id: str, service: FromDishka[JotformService], current_user: FromDishka[User]):
    return service.delete_jotform_form(form_id, current_user)


