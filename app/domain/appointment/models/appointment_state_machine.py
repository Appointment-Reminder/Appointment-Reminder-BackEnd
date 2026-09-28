from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

type Action[C] = Callable[[C], None]

class InvalidTransition(Exception):
    pass

@dataclass()
class StateMachine[S: Enum, E:Enum, C]:
    transitions: dict[tuple[S, E], tuple[S, Action[C]]] = field(default_factory=dict[dict[tuple[S, E], tuple[S, Action[C]]]])

    def add_transition(self, from_state: S, event: E,to_state: S, action: Action[C]) -> None:
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



class AppointmentState(Enum):
    NEW = auto()
    NEEDS_ASSIGNMENT = auto()
    PENDING = auto()
    PENDING_SELECTION = auto()
    PENDING_EDITING = auto()
    PENDING_REVIEW = auto()
    COMPLETED = auto()

class AppointmentEvent(Enum):
    CREATE = auto()
    ASSIGNMENT = auto()
    PHOTOSHOOT = auto()
    SELECTION = auto()
    EDITING = auto()
    REVIEW = auto()
    DONE = auto()

@dataclass
class AppointmentCtx:
    appointment_id: int
    audit: list[str] = field(default_factory=list[str])

appointment_sm: StateMachine[AppointmentState, AppointmentEvent, AppointmentCtx] = StateMachine()

def create(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> NEEDS_ASSIGNMENT")

def assign(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> PENDING")

def shoot(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> PHOTOSHOOT done PENDING SELECTION")

def select(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> SELECTION done PENDING_EDITING")

def edit(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> EDITING done PENDINGH REVIEW")

def review(ctx: AppointmentCtx) -> None:
    ctx.audit.append(f"{ctx.appointment_id} -> REVIEW done -> DONE")


appointment_sm.add_transition(
    AppointmentState.NEW,
    AppointmentEvent.CREATE,
    AppointmentState.NEEDS_ASSIGNMENT,
)

appointment_sm.add_transition(
    AppointmentState.NEEDS_ASSIGNMENT,
    AppointmentEvent.ASSIGNMENT,
    AppointmentState.PENDING,
)

appointment_sm.add_transition(
    AppointmentState.PENDING,
    AppointmentEvent.PHOTOSHOOT,
    AppointmentState.PENDING_SELECTION,
)

appointment_sm.add_transition(
    AppointmentState.PENDING_SELECTION,
    AppointmentEvent.SELECTION,
    AppointmentState.PENDING_EDITING,
)

appointment_sm.add_transition(
    AppointmentState.PENDING_EDITING,
    AppointmentEvent.EDITING,
    AppointmentState.PENDING_REVIEW,
)

appointment_sm.add_transition(
    AppointmentState.PENDING_REVIEW,
    AppointmentEvent.REVIEW,
    AppointmentState.COMPLETED,
)