from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.invitation_model import InvitationRead, InvitationCreate
from app.services import invitation_service
from app.services.user_service import get_current_user

invitation_router = APIRouter(
    prefix="/Business/{business_id}/invitations",
    tags=["invitations"],
)

@invitation_router.post("", response_model=InvitationRead, status_code=201)
def send_invitation(
        business_id: int,
        data: InvitationCreate,
        session: Session = Depends(get_session),
        current_user = Depends(get_current_user())
):
    """Send an invitation to join the business (Owner admin only)"""
    invitation, error = invitation_service.create_invitation(
        db=session,
        business_id=business_id,
        invitation_id = current_user.id,
        data=data
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    #TODO : send invitation email with invitation token here
    #eg send_invite_email(data.invitee_email, invitation.token)

    return invitation

@invitation_router.get("", response_model=list[InvitationRead], status_code=200)
def list_invitations(
    business_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all pending invitations for this business (owner/admin only)."""
    invitations, error = invitation_service.get_pending_invitations(
        db=session,
        business_id=business_id,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=403, detail=error)

    return invitations

@invitation_router.delete("/{invitation_id}", status_code=204)
def cancel_invitation(
    business_id: int,
    invitation_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Cancel a pending invitation (owner/admin only)."""
    success, error = invitation_service.cancel_invitation(
        db=session,
        invitation_id=invitation_id,
        business_id=business_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(status_code=400, detail=error)



# ── These two endpoints live outside the business prefix ─────────────────────
# because the invitee doesn't know the business_id, only their token

accept_decline_router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)


@accept_decline_router.post("/accept", status_code=200)
def accept_invitation(
    token: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Accept an invitation using the token from the invite email."""
    member, error = invitation_service.accept_invitation(
        db=session,
        token=token,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    return {"detail": "Invitation accepted, you are now a member of the business"}


@accept_decline_router.post("/decline", status_code=200)
def decline_invitation(
    token: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Decline an invitation using the token from the invite email."""

    success, error = invitation_service.decline_invitation(
        db=session,
        token=token,
        user_email=current_user.email,
    )
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"detail": "Invitation declined"}