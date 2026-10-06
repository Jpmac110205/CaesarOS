"""Validated contracts for model-generated content; Python owns execution facts."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ModelOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class RouteSelection(ModelOutput):
    workflow: Literal['', 'workout', 'study', 'interview', 'daily_plan', 'tutor', 'email',
                      'code', 'morning_digest', 'afternoon_checkin', 'evening_review']
    reason: str


class FocusItem(ModelOutput):
    title: str = Field(min_length=1)
    minutes: int = Field(ge=10, le=240)


class PlanningSelection(ModelOutput):
    priority_ids: list[str]
    focus_items: list[FocusItem]


class TutorResult(ModelOutput):
    summary: str = Field(min_length=1)
    practice_questions: list[str]


class EmailResult(ModelOutput):
    summary: str = Field(min_length=1)
    draft: str | None


class CodingResult(ModelOutput):
    title: str = Field(min_length=1)
    steps: list[str]
    artifact: str | None


class TestReview(ModelOutput):
    cases: list[str]


class CritiqueResult(ModelOutput):
    notes: list[str]
