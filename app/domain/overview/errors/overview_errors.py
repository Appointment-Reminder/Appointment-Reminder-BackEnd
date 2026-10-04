from app.domain.core.errors.errors import DomainError


class OverviewError(DomainError):
    """Base class for business overview errors"""


class InvalidPeriod(OverviewError):
    """The `from` day is after the `to` day, or the grouping is not day, week or month."""
