import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SELMoodLog(Base):
    """
    Social & Emotional Learning (SEL) log tracking child mood state
    across interactions (Happy, Curious, Silly, Sleepy).
    """
    __tablename__ = "sel_mood_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children_profiles.id", ondelete="CASCADE"), nullable=False)
    mood_selected = Column(String(20), nullable=False)  # 'happy', 'curious', 'silly', 'sleepy'
    logged_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    child = relationship("ChildProfile", back_populates="mood_logs")

    __table_args__ = (
        CheckConstraint(
            "mood_selected IN ('happy', 'curious', 'silly', 'sleepy')",
            name="ck_sel_mood"
        ),
        Index("ix_mood_logs_child", "child_id", logged_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<SELMoodLog(mood='{self.mood_selected}', logged_at='{self.logged_at}')>"
