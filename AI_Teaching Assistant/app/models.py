"""
Pydantic models for request/response validation.

Kept intentionally small: one model for what the student sends in,
one for what the API sends back.
"""

from pydantic import BaseModel, Field, field_validator

from app.config import MAX_QUESTION_LENGTH


class AskRequest(BaseModel):
    """What the browser sends to POST /api/ask."""

    registration_no: str = Field(..., description="Student registration number")
    question: str = Field(..., description="Student's Multivariable Control Systems question")

    @field_validator("registration_no")
    @classmethod
    def registration_no_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Registration number is required.")
        if len(value) > 50:
            raise ValueError("Registration number is too long.")
        return value

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question is required.")
        if len(value) > MAX_QUESTION_LENGTH:
            raise ValueError(
                f"Question is too long (max {MAX_QUESTION_LENGTH} characters)."
            )
        return value


class AskResponse(BaseModel):
    """What the API sends back to the browser."""

    answer: str
    subject: str


class InteractionOut(BaseModel):
    """One stored student interaction, as shown on the admin dashboard."""

    id: int
    registration_no: str
    subject: str
    question: str
    response: str
    model_used: str
    timestamp: str
    resolved: bool


class ResolveRequest(BaseModel):
    """What the admin page sends to mark an interaction resolved/unresolved."""

    resolved: bool
