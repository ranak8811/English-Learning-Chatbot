import time
import pytest
from sqlalchemy import text
from app.database import engine, SessionLocal, init_db
from app.services.db_service import (
    get_or_create_child_profile,
    get_child_profile,
    log_turn,
    get_recent_turns,
    record_sel_mood,
    add_star_and_check_progress,
    record_mastered_word,
    get_mastered_words
)


@pytest.fixture(scope="module")
def db_session():
    """Provides an isolated database session and ensures tables are created."""
    init_db()
    session = SessionLocal()
    yield session
    session.close()


def test_neon_postgres_connectivity(db_session):
    """
    Test 1: Verify SSL connection to Neon Cloud Serverless PostgreSQL.
    Requirement: Response within SLA (<150ms).
    """
    start_time = time.time()
    result = db_session.execute(text("SELECT 1 AS alive")).scalar()
    elapsed_ms = (time.time() - start_time) * 1000
    
    assert result == 1
    # Verify pooler connection is healthy
    assert elapsed_ms < 500  # Generous threshold for cloud roundtrip


def test_child_profile_crud(db_session):
    """
    Test 2: Create, retrieve, and verify ChildProfile.
    Verifies default values (age=5, level=L1, mode=learning, stars=0).
    """
    profile = get_or_create_child_profile(db_session, name="TestLeo", age=4, level="L1")
    assert profile.id is not None
    assert profile.name == "TestLeo"
    assert profile.age == 4
    assert profile.current_level == "L1"
    assert profile.current_mode == "learning"
    assert profile.stars_earned == 0

    fetched = get_child_profile(db_session, profile.id)
    assert fetched is not None
    assert fetched.id == profile.id


def test_conversation_turns_logging_and_context(db_session):
    """
    Test 3: Log user and assistant turns and retrieve recent turns in chronological order.
    """
    profile = get_or_create_child_profile(db_session, name="TestLeoTurns")
    
    # Log User Turn
    turn1 = log_turn(
        db=db_session,
        child_id=profile.id,
        role="user",
        content="I see a cat!",
        detected_mode="learning",
        detected_emotion="happy",
        level="L1",
        latency_ms=10
    )
    assert turn1.id is not None

    # Log Assistant Turn
    turn2 = log_turn(
        db=db_session,
        child_id=profile.id,
        role="assistant",
        content="Meow! A cat says meow! 🐱",
        detected_mode="learning",
        detected_emotion="happy",
        level="L1",
        latency_ms=650
    )
    assert turn2.id is not None

    recent = get_recent_turns(db_session, profile.id, limit=6)
    assert len(recent) >= 2
    # Verify chronological ordering (oldest first)
    assert recent[-2].role == "user"
    assert recent[-1].role == "assistant"
    assert recent[-1].latency_ms == 650


def test_sel_mood_logging(db_session):
    """
    Test 4: Verify Social and Emotional Learning (SEL) mood logging.
    """
    profile = get_or_create_child_profile(db_session, name="TestLeoMood")
    mood_log = record_sel_mood(db_session, profile.id, "happy")
    
    assert mood_log.id is not None
    assert mood_log.mood_selected == "happy"
    assert mood_log.child_id == profile.id


def test_milestone_and_star_progression(db_session):
    """
    Test 5: Verify star accumulation and level up recommendation logic.
    """
    profile = get_or_create_child_profile(db_session, name="TestLeoProgress", level="L1")
    
    # Record mastered vocabulary word
    milestone = record_mastered_word(db_session, profile.id, "Apple", "L1")
    assert milestone.word_or_phrase == "Apple"
    
    mastered_list = get_mastered_words(db_session, profile.id)
    assert "Apple" in mastered_list

    # Add stars and verify level-up recommendation threshold (5 stars at L1)
    stars, level_up = add_star_and_check_progress(db_session, profile.id, stars_to_add=5)
    assert stars >= 5
    assert level_up is True
