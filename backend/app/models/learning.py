import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class LearningMilestone(Base):
    """
    Tracks vocabulary words, phonic sounds, and grammar constructs
    that the child has successfully mastered.
    """
    __tablename__ = "learning_milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children_profiles.id", ondelete="CASCADE"), nullable=False)
    word_or_phrase = Column(String(100), nullable=False)
    level = Column(String(10), nullable=False)  # 'L1', 'L2', 'L3'
    mastered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    child = relationship("ChildProfile", back_populates="milestones")

    __table_args__ = (
        CheckConstraint("level IN ('L1', 'L2', 'L3')", name="ck_milestone_level"),
        Index("ix_milestones_child", "child_id"),
    )

    def __repr__(self) -> str:
        return f"<LearningMilestone(word='{self.word_or_phrase}', level='{self.level}')>"
