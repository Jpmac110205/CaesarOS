"""Compatibility import; state is now allocated per workflow, never on a class."""
from caesaros.state.workflow_state import WorkflowState as AgentState, new_state
__all__ = ['AgentState', 'new_state']
