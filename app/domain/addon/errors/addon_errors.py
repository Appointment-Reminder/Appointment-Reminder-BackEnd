from app.domain.core.errors.errors import DomainError


class AddonError(DomainError):
    """Base class for add-on errors"""


class NoAddonPriceInEffect(AddonError):
    """The add-on has no price whose effective date has passed, so it cannot be priced."""


class AppointmentAddonsLocked(AddonError):
    """The appointment is closed out (completed, canceled or refunded): its add-ons can no longer change."""
