from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1,description="Message envoyé à l'agent")
    thread_id: str | None = Field(default=None,description="Identifiant de la conversation")


class ReviewRequest(BaseModel):
    decision: Literal["approve", "reject"]


class AgentResponse(BaseModel):
    thread_id: str
    status: Literal[
        "completed",
        "review_required",
    ]

    answer: str | None = None

    review: dict[str, Any] | None = None