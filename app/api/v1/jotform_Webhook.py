from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db.session import get_session
from app.models.jotform_model import JotformProcessingResult
from app.services import jotform_service

jotform_router = APIRouter(
    prefix="/webhooks/jotform",
    tags=["jotform-webhooks"]
)

@jotform_router.post("/test", status_code=200)
async def test_webhook(request: Request):
    """
    Ultra-permissive test endpoint - accepts ANYTHING
    """
    try:
        # Print request details
        print("=" * 50)
        print("📝 REQUEST DETAILS:")
        print(f"Content-Type: {request.headers.get('content-type')}")
        print(f"Method: {request.method}")
        print("=" * 50)

        # Get raw body
        body = await request.body()
        print("📝 RAW BODY:")
        print(body.decode('utf-8'))
        print("=" * 50)

        # Try different parsing methods
        content_type = request.headers.get('content-type', '')

        if 'application/json' in content_type:
            data = await request.json()
            print("📝 Parsed as JSON:")
            print(data)
        elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            form = await request.form()
            print("📝 Parsed as FORM:")
            for key, value in form.items():
                print(f"{key}: {value}")
        else:
            print("⚠️ Unknown content type")

        print("=" * 50)

        return {"status": "received"}

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@jotform_router.post("/{photographer_id}", status_code=201, response_model=JotformProcessingResult)
async def receive_jotform_webhook(
        photographer_id: int,
        request: Request,
        session: Session = Depends(get_session),
):
    """Receive Jotform webhook submission for a specific photographer
    //TODO Do a secure id for photographer webhook so you can t create appointment for other people
    Each photographer gets a unique webhook URL:
    POST /webhooks/jotform/123"""

    try:
        if not jotform_service.JotformService.validate_photographer(session, photographer_id):
            raise HTTPException(status_code=404, detail="Photographer not found")

        print("processing jotform webhook")
        ##payload = await request.json()

        form_data = await request.form()
        form_dict = dict(form_data)

        print("=" * 50)
        print("📝 RECEIVED FORM DATA:")
        for key, value in form_dict.items():
            print(f"{key}: {value}")
        print("=" * 50)
        if 'rawRequest' not in form_dict or not form_dict['rawRequest']:
            print("❌ rawRequest is missing or empty!")
            return {"error": "rawRequest field is missing or empty"}

        appointment = jotform_service.JotformService.process_webhook(db= session, payload= form_dict, photographer_id= photographer_id)

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
