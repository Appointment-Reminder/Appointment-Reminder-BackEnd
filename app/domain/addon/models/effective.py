from datetime import datetime
from typing import Iterable, Optional, TypeVar

V = TypeVar("V")


def latest_in_effect(versions: Iterable[V], at: datetime) -> Optional[V]:
    """The version with the latest `effective_from` that has passed; None when none has."""
    started = [v for v in versions if v.effective_from <= at]
    return max(started, key=lambda v: v.effective_from, default=None)
