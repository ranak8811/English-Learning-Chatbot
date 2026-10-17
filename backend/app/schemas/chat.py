from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Incoming chat payload from the child/parent frontend client.
    """
    message: str = Field(..., description="Message spoken or typed by the child")
    child_id: Optional[UUID] = Field(default=None, description="Child profile UUID; created if null")
    current_level: Optional[str] = Field(default="L1", description="Current learning level: L1, L2, L3")
    selected_mood: Optional[str] = Field(default="happy", description="Active mood: happy, curious, silly, sleepy")


class ChatResponse(BaseModel):
    """
    Standardized response envelope returned to the client within <2s SLA.
    """
    reply: str = Field(..., description="Pedagogical, SEL-reinforced reply for audio playback & text display")
    child_id: UUID = Field(..., description="Child profile UUID")
    detected_mode: str = Field(..., description="Active mode: learning, conversation, engagement, support")
    detected_emotion: str = Field(..., description="Inferred emotion: happy, curious, silly, sleepy, sad")
    level: str = Field(..., description="Current/effective level: L1, L2, L3")
    stars_awarded: int = Field(default=0, description="Stars earned in this interaction turn")
    total_stars: int = Field(default=0, description="Total stars accumulated by child")
    level_up_recommended: bool = Field(default=False, description="True if child reached level milestone")
    mastered_word: Optional[str] = Field(default=None, description="Vocabulary word successfully used")
    latency_ms: int = Field(..., description="End-to-end response latency in milliseconds")
