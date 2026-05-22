from datetime import timedelta, datetime
from typing import Optional, List

from certifi import where
from sqlmodel import select, Session

from app.db.models.business import Business
from app.db.models.business_member import BusinessMember, MemberRole
from app.models.business_invitation import BusinessInvitation, InvitationStatus
from app.models.invitation_model import InvitationCreate
from app.services.business_service import _is_owner_or_admin

INVITATION_EXPIRY_DAYS = 7

def create_invitation(
        db: Session,
        business_id: int,
        inviter_id: int,
        data: InvitationCreate
) -> tuple[BusinessInvitation | None, str]:
    """ Create an invitation. Returns ( invitation, error_message). error_message is empty string on sucess."""
    if not _is_owner_or_admin(db, business_id, inviter_id):
        return None, " You don't have permission to create an invitation"

    business = db.get(Business, business_id)

    if not business or not business.is_active:
        return None, "Business not found or inactive"

    existing = db.exec(
        select(BusinessInvitation)
        .where(BusinessInvitation.business_id == business_id)
        .where(BusinessInvitation.invitee_email == data.invitee_email)
        .where(BusinessInvitation.status == InvitationStatus.PENDING)
    ).first()

    if existing:
        return None, "A pending invitation already exists for this email"

    # Check if user is already an active member (look up by email via User table if needed)
    # We'll do a lightweight check: if invitee_user_id is known and already a member
    from app.db.models.user import User
    invitee_user = db.exec(
        select(User).where(User.email == data.invitee_email)
    ).first()

    if invitee_user:
        already_member = db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .where(BusinessMember.user_id == invitee_user.user_id)
            .where(BusinessMember.is_active == True)
        ).first()
        if already_member:
            return None, "This user is already a member of the business"

    invitation = BusinessInvitation(
        business_id=business_id,
        invited_by = inviter_id,
        invitee_email = data.invitee_email,
        invitee_user_id = invitee_user.id if invitee_user else None,
        role = data.role,
        expires_at = datetime.utcnow() + timedelta(days=INVITATION_EXPIRY_DAYS)
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation,""


def get_invitation_by_token(db: Session, token: str) -> Optional[BusinessInvitation]:
    return db.exec(
        select(BusinessInvitation).where(BusinessInvitation.token == token)
    ).first()

def accept_invitation(
        db: Session,
        token: str,
        user_id: int,
        user_email: str,
) -> tuple[BusinessMember | None, str]:
    """Accept an invitation returns (new_member, error_message)."""
    invitation = get_invitation_by_token(db, token)

    if not invitation:
        return None, "Invitation not found"

    if invitation.status != InvitationStatus.PENDING:
        return None, f"Invitation is already {invitation.status}"

    if datetime.utcnow() > invitation.expires_at:
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        return None, "Invitation expired"

    if invitation.invitee_email.lower() != user_email.lower():
        return None, f"Invitation is already {invitation.invitee_email}"

    member = BusinessMember(
        business_id = invitation.business_id,
        user_id = user_id,
        role = invitation.role,
        invited_by = invitation.invitee_email,
        joined_at = datetime.utcnow(),
        is_active = True,
    )

    invitation.status = InvitationStatus.ACCEPTED
    invitation.invitee_user_id = user_id
    invitation.responded_at = datetime.utcnow()

    db.add(member)
    db.add(invitation)
    db.commit()
    db.refresh(member)
    return member,""


def decline_invitation(
        db: Session,
        token: str,
        user_email: str,
) -> tuple[bool, str]:
    """Decline an invitation returns (sucess, errorMessage)"""
    invitation = get_invitation_by_token(db, token)

    if not invitation:
        return False, "Invitation not found"

    if invitation.status != InvitationStatus.PENDING:
        return False, f"Invitation is already {invitation.status}"

    if invitation.invitee_email.lower() != user_email.lower():
        return False, f"Invitation was sent to a different email {invitation.invitee_email}"

    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = datetime.utcnow()

    db.commit()
    return True, ""

def cancel_invitation(
        db: Session,
        invitation_id: int,
        business_id: int,
        user_id: int,
) -> tuple[bool, str]:
    """Cancel a pending invitation (Owner adming only)"""
    if not _is_owner_or_admin(db, business_id, user_id):
        return False, "Yout don't have the permission to cancel invitation"

    invitation = get_invitation_by_token(db, invitation_id)

    if not invitation or invitation.business_id != business_id:
        return False, "Invitation not found"

    if invitation.status != InvitationStatus.PENDING:
        return False, f"Invitation is already {invitation.status}"

    invitation.status = InvitationStatus.CANCELLED
    db.commit()
    return True, ""

def get_pending_invitations(
        db:Session,
        business_id: int,
        user_id: int,
) -> tuple[List[BusinessInvitation] | None, str]:
    """List all pending invitations for a business (owner or admin only)"""
    if not _is_owner_or_admin(db, business_id, user_id):
        return None, "You don't have permission to see pending invitations"

    invitations = db.exec(
        select(BusinessInvitation)
        .where(BusinessInvitation.business_id == business_id)
        .where(BusinessInvitation.status == InvitationStatus.PENDING)
    ).all()

    return invitations, ""