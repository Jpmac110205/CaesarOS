from datetime import datetime
from typing import Any
from typing_extensions import TypedDict
from uuid import uuid4
from zoneinfo import ZoneInfo
from caesaros.state.models import RunRequest


class WorkflowState(TypedDict):
    id: str
    revision: int
    user_input: str
    requested_workflow: str
    selected_workflow: str
    intent: str
    confidence_scores: dict[str, float | None]
    decision: dict[str, Any]
    workflow_status: str
    current_agent: str | None
    current_time: str
    timezone: str
    created_at: str
    finished_at: str | None
    agent_sequence: list[str]
    cursor: int
    agents: dict[str, dict]
    calendar_events: list[dict]
    tasks: list[dict]
    emails: list[dict]
    memory_context: list[dict]
    retrieved_documents: list[dict]
    fitness_data: dict
    github_context: dict
    planner_output: dict
    tutor_output: dict
    fitness_output: dict
    email_output: dict
    code_output: dict
    tool_results: list[dict]
    sources: list[dict]
    events: list[dict]
    proposed_actions: list[dict]
    final_response: str
    metrics: dict
    error: str | None


TERMINAL = {'completed', 'awaiting_approval', 'needs_clarification', 'failed', 'cancelled'}
AGENTS = ['email', 'planner', 'tutor', 'fitness', 'code']


def new_state(request: RunRequest, timezone: str) -> WorkflowState:
    now = datetime.now(ZoneInfo(timezone)).isoformat()
    return WorkflowState(
        id=uuid4().hex, revision=0, user_input=request.user_input.strip(),
        requested_workflow=request.workflow, selected_workflow='', intent='',
        confidence_scores={}, decision={}, workflow_status='queued', current_agent=None,
        current_time=now, timezone=timezone, created_at=now, finished_at=None,
        agent_sequence=[], cursor=0,
        agents={name: {'status': 'idle', 'summary': '', 'duration_ms': 0, 'attempts': 0} for name in AGENTS},
        calendar_events=[], tasks=[], emails=[], memory_context=[], retrieved_documents=[],
        fitness_data={}, github_context={}, planner_output={}, tutor_output={},
        fitness_output={}, email_output={}, code_output={}, tool_results=[], sources=[],
        events=[], proposed_actions=[], final_response='',
        metrics={'duration_ms': 0, 'input_tokens': 0, 'output_tokens': 0, 'retries': 0,
                 'model_calls': 0, 'reasoner': 'openai', 'provider_calls': []}, error=None)
