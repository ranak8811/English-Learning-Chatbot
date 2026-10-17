import pytest
from app.services.mode_detector import detect_child_mode
from app.services.sel_engine import (
    sanitize_sel_response,
    format_sel_reinforcement,
    detect_emotion
)
from app.services.learning_engine import (
    extract_mastered_word,
    evaluate_learning_step
)


# ==========================================
# 1. Child Mode Detection Tests (FR-MOD-01..05)
# ==========================================

def test_mode_detector_support():
    """Child expressing fatigue, frustration, or sadness must trigger Support mode."""
    assert detect_child_mode("I am so tired, my eyes hurt") == "support"
    assert detect_child_mode("This is too hard, I don't know") == "support"
    assert detect_child_mode("I'm sad, I want mommy") == "support"
    assert detect_child_mode("sleep", selected_mood="sleepy") == "support"


def test_mode_detector_engagement():
    """Child making silly sounds, giggling, or playing games must trigger Engagement mode."""
    assert detect_child_mode("Rawrrr I am a big dinosaur haha") == "engagement"
    assert detect_child_mode("beep boop vroom vroom") == "engagement"
    assert detect_child_mode("hahahahahaha") == "engagement"
    assert detect_child_mode("tell me a funny joke") == "engagement"


def test_mode_detector_conversation():
    """Child sharing personal life or chatting casually must trigger Conversation mode."""
    assert detect_child_mode("My name is Leo and I have a puppy") == "conversation"
    assert detect_child_mode("I love playing in the park with my dad") == "conversation"
    assert detect_child_mode("What is your favorite animal, Buddy?") == "conversation"


def test_mode_detector_learning():
    """Child practicing vocabulary or answering lesson questions defaults to Learning mode."""
    assert detect_child_mode("Cat") == "learning"
    assert detect_child_mode("The dog is red") == "learning"
    assert detect_child_mode("Apple") == "learning"


# ==========================================
# 2. Social & Emotional Learning (SEL) Tests (FR-SEL-01..02)
# ==========================================

def test_sel_negative_language_sanitization():
    """Confirms no negative or punitive language can reach the child."""
    punitive_input = "No, that's wrong! You are incorrect."
    sanitized = sanitize_sel_response(punitive_input)
    assert "wrong" not in sanitized.lower()
    assert "incorrect" not in sanitized.lower()
    assert "try" in sanitized.lower()

    mistake_input = "You made a mistake on this word."
    sanitized_mistake = sanitize_sel_response(mistake_input)
    assert "Mistakes help our brain grow" in sanitized_mistake


def test_sel_format_reinforcement():
    """Verifies star praise, support comfort, and engagement emojis."""
    # Star earned praise
    reply_star = format_sel_reinforcement("Super job!", mode="learning", mood="happy", awarded_star=True)
    assert "star" in reply_star.lower() or "🌟" in reply_star

    # Support mode soothing
    reply_support = format_sel_reinforcement("Let's take a rest.", mode="support", mood="sleepy")
    assert "💛" in reply_support or "take your time" in reply_support.lower()


def test_emotion_detection():
    """Infers child emotions from message and mood picker."""
    assert detect_emotion("I'm crying", "happy") == "sad"
    assert detect_emotion("I'm so sleepy", "happy") == "sleepy"
    assert detect_emotion("haha that is funny", "happy") == "silly"
    assert detect_emotion("Why does the sun shine?", "curious") == "curious"


# ==========================================
# 3. Progressive Learning Engine Tests (FR-LRN-01..04)
# ==========================================

def test_extract_mastered_words():
    """Extracts level-appropriate vocabulary words."""
    assert extract_mastered_word("I see a cat!", "L1") == "Cat"
    assert extract_mastered_word("The big dog runs", "L2") == "Big Dog"
    assert extract_mastered_word("The puppy jumped over the fence", "L3") == "Expressive Sentence"


def test_learning_step_and_level_promotion():
    """Tests star reward and 5-star promotion threshold from L1 to L2."""
    level, stars_to_award, level_up, mastered = evaluate_learning_step(
        current_level="L1",
        stars_earned=4,
        message="I love my Cat!",
        mode="learning"
    )
    assert level == "L1"
    assert stars_to_award == 1
    assert mastered == "Cat"
    # 4 stars + 1 awarded star = 5 stars -> triggers promotion recommendation!
    assert level_up is True


def test_learning_step_difficulty_adaptation():
    """Tests graceful level adaptation when child expresses difficulty."""
    level, stars, level_up, _ = evaluate_learning_step(
        current_level="L3",
        stars_earned=2,
        message="This is too hard for me, I can't do it",
        mode="support"
    )
    # Adapts down from L3 to L2 to prevent child frustration
    assert level == "L2"
    assert stars == 0
    assert level_up is False
