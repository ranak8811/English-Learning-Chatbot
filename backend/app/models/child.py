import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ChildProfile(Base):
    """
    Core child entity representing the young learner (Ages 3-7).
    Tracks current pedagogical level, interaction mode, and rewards.
    """
    __tablename__ = "children_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, default="Little Explorer")
    age = Column(Integer, nullable=False, default=5)
    current_level = Column(String(10), nullable=False, default="L1")
    current_mode = Column(String(20), nullable=False, default="learning")
    stars_earned = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    conversation_turns = relationship("ConversationTurn", back_populates="child", cascade="all, delete-orphan")
    milestones = relationship("LearningMilestone", back_populates="child", cascade="all, delete-orphan")
    mood_logs = relationship("SELMoodLog", back_populates="child", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("age >= 2 AND age <= 7", name="ck_child_age"),
        CheckConstraint("current_level IN ('L1', 'L2', 'L3')", name="ck_child_level"),
        CheckConstraint(
            "current_mode IN ('learning', 'conversation', 'engagement', 'support')",
            name="ck_child_mode"
        ),
        CheckConstraint("stars_earned >= 0", name="ck_child_stars"),
    )

    def __repr__(self) -> str:
        return f"<ChildProfile(id={self.id}, name='{self.name}', level='{self.current_level}', stars={self.stars_earned})>"
