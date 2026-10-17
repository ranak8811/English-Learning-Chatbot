from typing import Tuple, Optional, List


LEVEL_1_TARGET_WORDS = [
    "cat", "dog", "sun", "apple", "ball", "cow", "red", "blue", "yellow",
    "cup", "star", "fish", "tree", "bird", "hat", "car", "duck", "bear"
]

LEVEL_2_TARGET_PHRASES = [
    "big dog", "red apple", "two cats", "the bird flies", "i like apples",
    "blue ball", "hot sun", "happy baby", "green tree", "fast car", "run fast"
]


def extract_mastered_word(message: str, level: str) -> Optional[str]:
    """
    Checks if the child's utterance successfully uses or repeats a target vocabulary word.
    """
    text = (message or "").strip().lower()

    if level == "L1":
        for word in LEVEL_1_TARGET_WORDS:
            # Word boundary match
            if word in text:
                return word.capitalize()

    elif level == "L2":
        for phrase in LEVEL_2_TARGET_PHRASES:
            if phrase in text:
                return phrase.title()
        # Also check Level 1 words used in 2-3 word combinations
        words = text.split()
        if 2 <= len(words) <= 5:
            for word in LEVEL_1_TARGET_WORDS:
                if word in words:
                    return f"Phrase with {word.capitalize()}"

    elif level == "L3":
        # At Level 3, producing a sentence of 3+ words counts as mastery
        words = text.split()
        if len(words) >= 3:
            return "Expressive Sentence"

    return None


def evaluate_learning_step(
    current_level: str,
    stars_earned: int,
    message: str,
    mode: str
) -> Tuple[str, int, bool, Optional[str]]:
    """
    Evaluates child's response for pedagogical progression:
    Returns:
    - effective_level (e.g., "L1", "L2", "L3")
    - stars_to_award (0 or 1)
    - level_up_recommended (True if threshold reached)
    - mastered_item (word or phrase if mastered)
    """
    text = (message or "").lower()
    effective_level = current_level

    # Check for child requesting difficulty drop
    if any(phrase in text for phrase in ["too hard", "so hard", "very hard", "cant do this", "can't do"]):
        if current_level == "L3":
            effective_level = "L2"
        elif current_level == "L2":
            effective_level = "L1"
        return effective_level, 0, False, None

    # Check for vocabulary mastery
    mastered_item = extract_mastered_word(message, effective_level)

    # Award star if:
    # 1. Target word was used, OR
    # 2. Child is actively answering in learning mode with > 1 word
    stars_to_award = 0
    if mastered_item or (mode == "learning" and len(text.split()) >= 1):
        stars_to_award = 1

    new_total_stars = stars_earned + stars_to_award
    level_up_recommended = False

    # Check milestone promotion thresholds
    if effective_level == "L1" and new_total_stars >= 5:
        level_up_recommended = True
    elif effective_level == "L2" and new_total_stars >= 10:
        level_up_recommended = True

    return effective_level, stars_to_award, level_up_recommended, mastered_item
