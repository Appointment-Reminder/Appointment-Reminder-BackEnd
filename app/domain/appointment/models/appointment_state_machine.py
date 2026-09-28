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

    def next_transition(self, state: S, event: E) -> tuple[S, Action[C]]:
        try:
            return self.transitions[(state, event)]
        except KeyError as e:
            raise InvalidTransition(f"Cannot {event.name} when {state.name}") from e

    def handle(self, ctx: C, state: S, event: E) -> S:
        next_state, action  = self.next_transition(state, event)
        action(ctx)
        return next_state

    def transition(self, from_state: S, event: E, to_state: S):
        def decorator(func: Action[C]) -> Action[C]:
            self.add_transition(from_state, event, to_state, func)
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

class AppointmentEvent(str, Enum):
    CREATE = "create"
    ASSIGN = "assign"
    PHOTOSHOOT = "photoshoot"
    SELECTION = "selection"
    EDITING = "editing"
    REVIEW = "review"

@dataclass
class AppointmentCtx:
    appointment_id: Optional[int]
    audit: list[str] = field(default_factory=list[str])

appointment_sm: StateMachine[AppointmentStatus, AppointmentEvent, AppointmentCtx] = StateMachine()

@appointment_sm.transition(AppointmentStatus.New, AppointmentEvent.CREATE, AppointmentStatus.NEEDS_ASSIGNMENT)
def create(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> NEEDS_ASSIGNMENT")

@appointment_sm.transition(AppointmentStatus.NEEDS_ASSIGNMENT, AppointmentEvent.ASSIGN, AppointmentStatus.PENDING)
def assign(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> PENDING")

@appointment_sm.transitions(AppointmentStatus.PENDING, AppointmentEvent.PHOTOSHOOT, AppointmentStatus.PENDING_SELECTION)
def shoot(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> PHOTOSHOOT done PENDING SELECTION")

@appointment_sm.transitions(AppointmentStatus.PENDING_SELECTION, AppointmentEvent.SELECTION, AppointmentStatus.PENDING_EDITING)
def select(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> SELECTION done PENDING_EDITING")

@appointment_sm.transitions(AppointmentStatus.PENDING_EDITING, AppointmentEvent.EDITING, AppointmentEvent.REVIEW)
def edit(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> EDITING done PENDINGH REVIEW")

@appointment_sm.transitions(AppointmentStatus.PENDING_REVIEW, AppointmentEvent.REVIEW, AppointmentStatus.COMPLETED)
def review(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> REVIEW done -> DONE")