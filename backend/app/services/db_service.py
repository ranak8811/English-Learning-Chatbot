import uuid
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.child import ChildProfile
from app.models.conversation import ConversationTurn
from app.models.learning import LearningMilestone
from app.models.sel import SELMoodLog


def get_or_create_child_profile(
    db: Session,
    name: str = "Leo",
    age: int = 5,
    level: str = "L1"
) -> ChildProfile:
    """
    Retrieves existing child profile or creates a default profile for the session.
    Ages 2-7 supported, default level L1 (Seedling).
    """
    profile = db.query(ChildProfile).filter(ChildProfile.name == name).first()
    if not profile:
        profile = ChildProfile(
            name=name,
            age=age,
            current_level=level,
            current_mode="learning",
            stars_earned=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_child_profile(db: Session, child_id: uuid.UUID) -> Optional[ChildProfile]:
    """Retrieves a child profile by UUID."""
    return db.query(ChildProfile).filter(ChildProfile.id == child_id).first()


def log_turn(
    db: Session,
    child_id: uuid.UUID,
    role: str,
    content: str,
    detected_mode: Optional[str] = None,
    detected_emotion: Optional[str] = None,
    level: str = "L1",
    latency_ms: Optional[int] = None
) -> ConversationTurn:
    """
    Persists a single conversational turn with mode detection and latency metrics.
    """
    turn = ConversationTurn(
        child_id=child_id,
        role=role,
        content=content,
        detected_mode=detected_mode,
        detected_emotion=detected_emotion,
        level=level,
        latency_ms=latency_ms
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn


def get_recent_turns(
    db: Session,
    child_id: uuid.UUID,
    limit: int = 6
) -> List[ConversationTurn]:
    """
    Retrieves the last N turns for short-term conversational context.
    Returns in chronological order (oldest to newest) for prompt context.
    """
    turns = (
        db.query(ConversationTurn)
        .filter(ConversationTurn.child_id == child_id)
        .order_by(desc(ConversationTurn.created_at))
        .limit(limit)
        .all()
    )
    return list(reversed(turns))


def record_sel_mood(
    db: Session,
    child_id: uuid.UUID,
    mood: str
) -> SELMoodLog:
    """Records an emotional check-in for the child (happy, curious, silly, sleepy)."""
    mood_log = SELMoodLog(
        child_id=child_id,
        mood_selected=mood.lower()
    )
    db.add(mood_log)
    db.commit()
    db.refresh(mood_log)
    return mood_log


def add_star_and_check_progress(
    db: Session,
    child_id: uuid.UUID,
    stars_to_add: int = 1
) -> Tuple[int, bool]:
    """
    Increments star reward count and checks if the child has unlocked level progression.
    Threshold: Every 5 stars at current level unlocks progression recommendation.
    """
    profile = get_child_profile(db, child_id)
    if not profile:
        return 0, False

    profile.stars_earned += stars_to_add
    
    # Milestone threshold for leveling up
    level_up_recommended = False
    if profile.current_level == "L1" and profile.stars_earned >= 5:
        level_up_recommended = True
    elif profile.current_level == "L2" and profile.stars_earned >= 10:
        level_up_recommended = True

    db.commit()
    db.refresh(profile)
    return profile.stars_earned, level_up_recommended


def record_mastered_word(
    db: Session,
    child_id: uuid.UUID,
    word: str,
    level: str
) -> LearningMilestone:
    """Records a vocabulary word or phrase that the child successfully used."""
    # Check if already mastered to prevent duplicates
    existing = (
        db.query(LearningMilestone)
        .filter(
            LearningMilestone.child_id == child_id,
            LearningMilestone.word_or_phrase == word.strip().capitalize()
        )
        .first()
    )
    if existing:
        return existing

    milestone = LearningMilestone(
        child_id=child_id,
        word_or_phrase=word.strip().capitalize(),
        level=level
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def get_mastered_words(db: Session, child_id: uuid.UUID) -> List[str]:
    """Retrieves all words mastered by the child."""
    milestones = (
        db.query(LearningMilestone)
        .filter(LearningMilestone.child_id == child_id)
        .all()
    )
    return [m.word_or_phrase for m in milestones]
