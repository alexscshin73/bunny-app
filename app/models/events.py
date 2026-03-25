from typing import Any, Literal

from pydantic import BaseModel, Field


class ClientControlEvent(BaseModel):
    type: Literal["start", "stop", "ping"]
    sample_rate: int | None = None
    language: str | None = None


class ServerEvent(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)

