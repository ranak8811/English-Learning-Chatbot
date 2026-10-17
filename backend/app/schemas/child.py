from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChildCreateRequest(BaseModel):
    name: str = Field(default="Little Explorer", min_length=1, max_length=50)
    age: int = Field(default=5, ge=2, le=7)
    current_level: str = Field(default="L1", pattern="^(L1|L2|L3)$")


class ChildProfileResponse(BaseModel):
    id: UUID
    name: str
    age: int
    current_level: str
    current_mode: str
    stars_earned: int
    mastered_words: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MoodRecordRequest(BaseModel):
    mood: str = Field(..., pattern="^(happy|curious|silly|sleepy)$")


class TurnHistoryResponse(BaseModel):
    id: UUID
    role: str
    content: str
    detected_mode: Optional[str] = None
    level: str
    latency_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
