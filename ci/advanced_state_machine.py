"""Advanced State Machine for system orchestration with hierarchical states."""
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """Core system states."""
    INITIALIZATION = "init"
    IDLE = "idle"
    PROCESSING = "processing"
    OPTIMIZING = "optimizing"
    FAULT_RECOVERY = "fault_recovery"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class TransitionType(Enum):
    """Types of state transitions."""
    AUTOMATIC = "automatic"
    CONDITIONAL = "conditional"
    MANUAL = "manual"
    EMERGENCY = "emergency"


@dataclass
class StateTransition:
    """Represents a transition between states."""
    from_state: SystemState
    to_state: SystemState
    transition_type: TransitionType = TransitionType.AUTOMATIC
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    async def execute(self) -> bool:
        """Execute the transition."""
        try:
            if self.condition and not await self._async_call(self.condition):
                return False
            if self.action:
                await self._async_call(self.action)
            return True
        except Exception as e:
            logger.error(f"Transition execution failed: {e}")
            return False

    async def _async_call(self, func: Callable) -> Any:
        """Call function with async support."""
        if asyncio.iscoroutinefunction(func):
            return await func()
        return func()


@dataclass
class HierarchicalState:
    """Hierarchical state with substates."""
    state: SystemState
    parent_state: Optional['HierarchicalState'] = None
    substates: List['HierarchicalState'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def get_full_path(self) -> str:
        """Get the full hierarchical path."""
        if self.parent_state:
            return f"{self.parent_state.get_full_path()}/{self.state.value}"
        return self.state.value

    def add_substate(self, substate: 'HierarchicalState') -> None:
        """Add a substate."""
        substate.parent_state = self
        self.substates.append(substate)


class AdvancedStateMachine:
    """State machine with advanced features for system orchestration."""

    def __init__(self, name: str = "StateMachine-001"):
        self.name = name
        self.current_state = SystemState.INITIALIZATION
        self.previous_state = None
        self.transitions: Dict[Tuple[SystemState, SystemState], StateTransition] = {}
        self.transition_history: List[StateTransition] = []
        self.state_handlers: Dict[SystemState, List[Callable]] = {}
        self.state_timers: Dict[SystemState, float] = {}
        self.hierarchical_states: Dict[SystemState, HierarchicalState] = {}
        self.failure_count = 0
        self.max_failures = 5
        self._lock = asyncio.Lock()
        logger.info(f"Initialized {self.name}")

    def register_transition(
        self,
        from_state: SystemState,
        to_state: SystemState,
        transition_type: TransitionType = TransitionType.AUTOMATIC,
        condition: Optional[Callable] = None,
        action: Optional[Callable] = None
    ) -> None:
        """Register a state transition."""
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            transition_type=transition_type,
            condition=condition,
            action=action
        )
        self.transitions[(from_state, to_state)] = transition
        logger.debug(f"Registered transition: {from_state.value} -> {to_state.value}")

    def register_state_handler(
        self,
        state: SystemState,
        handler: Callable
    ) -> None:
        """Register a handler for state entry/exit."""
        if state not in self.state_handlers:
            self.state_handlers[state] = []
        self.state_handlers[state].append(handler)
        logger.debug(f"Registered handler for {state.value}")

    async def transition_to(
        self,
        target_state: SystemState,
        force: bool = False
    ) -> bool:
        """Transition to a target state."""
        async with self._lock:
            if not force and (self.current_state, target_state) not in self.transitions:
                logger.warning(f"No transition defined: {self.current_state.value} -> {target_state.value}")
                return False

            transition = self.transitions.get((self.current_state, target_state))
            if transition and not await transition.execute():
                self.failure_count += 1
                if self.failure_count > self.max_failures:
                    await self._enter_error_state("Max failures exceeded")
                return False

            self.previous_state = self.current_state
            self.current_state = target_state
            self.failure_count = 0
            self.transition_history.append(transition or StateTransition(self.previous_state, target_state))

            # Execute state handlers
            await self._execute_state_handlers(target_state)
            logger.info(f"Transitioned to {target_state.value}")
            return True

    async def _execute_state_handlers(self, state: SystemState) -> None:
        """Execute all handlers for a state."""
        handlers = self.state_handlers.get(state, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Handler execution error: {e}")

    async def _enter_error_state(self, reason: str) -> None:
        """Enter error state due to failure."""
        logger.critical(f"Entering error state: {reason}")
        self.current_state = SystemState.ERROR

    def create_hierarchical_state(
        self,
        state: SystemState,
        parent_state: Optional[SystemState] = None
    ) -> HierarchicalState:
        """Create a hierarchical state."""
        h_state = HierarchicalState(state=state)
        
        if parent_state and parent_state in self.hierarchical_states:
            parent_h_state = self.hierarchical_states[parent_state]
            parent_h_state.add_substate(h_state)
        
        self.hierarchical_states[state] = h_state
        return h_state

    def get_state_hierarchy(self) -> Dict[str, Any]:
        """Get the complete state hierarchy."""
        hierarchy = {}
        for state, h_state in self.hierarchical_states.items():
            hierarchy[state.value] = {
                "path": h_state.get_full_path(),
                "substates": [s.state.value for s in h_state.substates],
                "properties": h_state.properties
            }
        return hierarchy

    def get_transition_matrix(self) -> Dict[str, List[str]]:
        """Get the state transition matrix."""
        matrix = {state.value: [] for state in SystemState}
        for (from_state, to_state) in self.transitions.keys():
            matrix[from_state.value].append(to_state.value)
        return matrix

    def get_status(self) -> Dict[str, Any]:
        """Get current state machine status."""
        return {
            "name": self.name,
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "transition_count": len(self.transition_history),
            "failure_count": self.failure_count,
            "timestamp": datetime.now().isoformat()
        }

    def reset(self) -> None:
        """Reset the state machine."""
        self.current_state = SystemState.INITIALIZATION
        self.previous_state = None
        self.failure_count = 0
        self.transition_history = []
        logger.info(f"{self.name} reset")


if __name__ == "__main__":
    import json

    async def main():
        # Create state machine
        sm = AdvancedStateMachine("MainOrchestrator")
        
        # Register transitions
        sm.register_transition(SystemState.INITIALIZATION, SystemState.IDLE)
        sm.register_transition(SystemState.IDLE, SystemState.PROCESSING)
        sm.register_transition(SystemState.PROCESSING, SystemState.OPTIMIZING)
        sm.register_transition(SystemState.PROCESSING, SystemState.FAULT_RECOVERY)
        sm.register_transition(SystemState.FAULT_RECOVERY, SystemState.IDLE)
        sm.register_transition(SystemState.IDLE, SystemState.SHUTDOWN)
        
        # Transition sequence
        await sm.transition_to(SystemState.IDLE)
        await sm.transition_to(SystemState.PROCESSING)
        await sm.transition_to(SystemState.OPTIMIZING)
        await sm.transition_to(SystemState.IDLE)
        
        # Get status
        status = sm.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")
        
        # Get transition matrix
        matrix = sm.get_transition_matrix()
        print(f"Transition Matrix: {json.dumps(matrix, indent=2)}")

    asyncio.run(main())
