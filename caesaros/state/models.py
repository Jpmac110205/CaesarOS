from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Workflow = Literal['auto', 'workout', 'study', 'interview', 'daily_plan', 'tutor',
                   'email', 'code', 'morning_digest', 'afternoon_checkin', 'evening_review']


class RunRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    user_input: str = Field(min_length=1, max_length=4000)
    workflow: Workflow = 'auto'


class ApprovalRequest(BaseModel):
    decision: Literal['approve', 'reject']


class TaskUpdate(BaseModel):
    completed: bool


class ScheduleUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    enabled: bool
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
