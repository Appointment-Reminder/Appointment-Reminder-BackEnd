from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Iterable, Optional

from app.domain.appointment.errors.appointment_error import AppointmentError

type Action[C] = Callable[[C], None]

class InvalidTransition(AppointmentError):
    pass

@dataclass()
class StateMachine[S: Enum, E:Enum, C]:
    transitions: dict[tuple[S, E], tuple[S, Action[C]]] = field(default_factory=dict[dict[tuple[S, E], tuple[S, Action[C]]]])

    def add_transition(self, from_state: S, event: E, to_state: S, action: Action[C]) -> None:
        self.transitions[(from_state, event)] = (to_state, action)

    def handle(self, ctx: C, state: S, event: E) -> S:
        try:
            next_state, action = self.transitions[(state, event)]
        except KeyError as e:
            raise InvalidTransition(f"Cannot {event.name} when {state.name}") from e
        action(ctx)
        return next_state

    def transition(self, from_state: S | Iterable[S], event: E, to_state: S):
        if isinstance(from_state, Enum):
            from_state = (from_state,)

        def decorator(func: Action[C]) -> Action[C]:
            for s in from_state:
                self.add_transition(s, event, to_state, func)
            return func

        return decorator


class AppointmentStatus(str, Enum):
    NEW = "new"
    NEEDS_ASSIGNMENT = "needs_assignment"
    PENDING = "pending"
    PENDING_SELECTION = "pending_selection"
    PENDING_EDITING = "pending_editing"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REFUNDED = "refunded"

class AppointmentEvent(str, Enum):
    CREATE = "create"
    ASSIGN = "assign"
    PHOTOSHOOT = "photoshoot"
    SELECTION = "selection"
    EDITING = "editing"
    REVIEW = "review"
    CANCEL = "canceled"
    REFUND = "refund"
    UNASSIGN = "unassigned"
    REMOVE_SELECTION = "remove_selection"
    REMOVE_EDITING = "remove_editing"

@dataclass
class AppointmentCtx:
    appointment_id: Optional[int]
    audit: list[str] = field(default_factory=list[str])

appointment_sm: StateMachine[AppointmentStatus, AppointmentEvent, AppointmentCtx] = StateMachine()

S, E = AppointmentStatus, AppointmentEvent


@appointment_sm.transition(S.NEW, E.CREATE, S.NEEDS_ASSIGNMENT)
def _create(ctx): ctx.audit.append(f"{ctx.appointment_id} -> NEEDS_ASSIGNMENT")

@appointment_sm.transition(S.NEEDS_ASSIGNMENT, E.ASSIGN, S.PENDING)
def _assign(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING")

@appointment_sm.transition(S.NEEDS_ASSIGNMENT, E.ASSIGN, S.PENDING)
def _assign(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING")

@appointment_sm.transition(S.PENDING, E.PHOTOSHOOT, S.PENDING_SELECTION)
def _shoot(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING_SELECTION")

@appointment_sm.transition(S.PENDING_SELECTION, E.SELECTION, S.PENDING_EDITING)
def _select(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING_EDITING")

@appointment_sm.transition(S.PENDING_EDITING, E.EDITING, S.PENDING_REVIEW)
def _edit(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING_REVIEW")

@appointment_sm.transition(S.PENDING_REVIEW, E.REVIEW, S.COMPLETED)
def _review(ctx): ctx.audit.append(f"{ctx.appointment_id} -> COMPLETED")

@appointment_sm.transition(S.PENDING_REVIEW, E.REMOVE_EDITING, S.PENDING_EDITING)
def _unedit(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING_REVIEW")

@appointment_sm.transition(S.PENDING_EDITING, E.REMOVE_SELECTION, S.PENDING_SELECTION)
def _unselect(ctx): ctx.audit.append(f"{ctx.appointment_id} -> PENDING_SELECTION")

@appointment_sm.transition( (
    S.NEW,
    S.PENDING_SELECTION,
    S.PENDING,
    S.PENDING_EDITING,
    S.PENDING_REVIEW,
    S.NEEDS_ASSIGNMENT,
    S.COMPLETED,),
    E.CANCEL,
    S.CANCELED)
def _cancel(ctx): ctx.audit.append(f"{ctx.appointment_id} -> CANCELED")

@appointment_sm.transition( (
    S.NEW,
    S.PENDING_SELECTION,
    S.PENDING,
    S.PENDING_EDITING,
    S.PENDING_REVIEW,
    S.NEEDS_ASSIGNMENT,
    S.COMPLETED,),
    E.REFUND,
    S.REFUNDED)
def _cancel(ctx): ctx.audit.append(f"{ctx.appointment_id} -> REFUND")