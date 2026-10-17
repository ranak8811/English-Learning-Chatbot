import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ConversationTurn(Base):
    """
    Log of each message turn exchanged between the child and the chatbot.
    Stores pedagogical level, detected mode/emotion, and response latency.
    """
    __tablename__ = "conversation_turns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children_profiles.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    detected_mode = Column(String(20), nullable=True)  # 'learning', 'conversation', 'engagement', 'support'
    detected_emotion = Column(String(20), nullable=True)  # 'happy', 'curious', 'silly', 'sleepy'
    level = Column(String(10), nullable=False, default="L1")
    latency_ms = Column(Integer, nullable=True)  # Roundtrip time in ms for SLA auditing
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    child = relationship("ChildProfile", back_populates="conversation_turns")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="ck_turn_role"),
        Index("ix_turns_child_created", "child_id", created_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<ConversationTurn(id={self.id}, role='{self.role}', mode='{self.detected_mode}', latency={self.latency_ms}ms)>"
