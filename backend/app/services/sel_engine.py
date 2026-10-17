import re
from typing import Tuple


NEGATIVE_PATTERNS = [
    (r"\b(that is|that's|you are)\s+(wrong|incorrect|not right|bad)\b", "Great try! Let's say it together:"),
    (r"\bno,\s+that('s|\s+is)\s+not\b", "Almost! Let's listen together:"),
    (r"\bwrong!\b", "Good try! 🌟"),
    (r"\bincorrect!\b", "Super effort! ⭐"),
    (r"\byou made a mistake\b", "Mistakes help our brain grow! 🌱"),
]

GROWTH_MINDSET_PRAISES = [
    "You are practicing so hard! 🌟",
    "I love how curious you are! 🧐",
    "High five for trying! ✋",
    "Your brain is getting stronger! 💪",
    "You're a super English explorer! 🚀"
]


def sanitize_sel_response(response_text: str) -> str:
    """
    Guarantees no punitive or negative language reaches the child.
    Replaces negative corrections with growth mindset framing.
    """
    clean = response_text.strip()
    for pattern, replacement in NEGATIVE_PATTERNS:
        clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)
    return clean


def format_sel_reinforcement(
    reply: str,
    mode: str,
    mood: str,
    awarded_star: bool = False
) -> str:
    """
    Applies Social & Emotional Learning (SEL) post-processing:
    - Injects star celebration if awarded.
    - Adds emotional comfort if in support mode.
    - Sanitizes any potential negative corrections.
    """
    sanitized = sanitize_sel_response(reply)

    # In support mode, guarantee loving, soothing tone
    if mode == "support":
        if "💛" not in sanitized and "🤗" not in sanitized:
            sanitized = f"{sanitized} Take your time, you are doing great! 💛"
        return sanitized

    # In engagement mode, guarantee playful emoji
    if mode == "engagement":
        if "🎈" not in sanitized and "🎉" not in sanitized and "🐱" not in sanitized and "🐶" not in sanitized:
            sanitized = f"{sanitized} 🎈"
        return sanitized

    # If star was earned, celebrate it
    if awarded_star and "⭐" not in sanitized and "🌟" not in sanitized:
        sanitized = f"{sanitized} You earned a shiny star! 🌟"

    return sanitized


def detect_emotion(message: str, selected_mood: str = "happy") -> str:
    """
    Infers the emotional state of the child combining the selected mood button and utterance.
    """
    text = (message or "").lower()

    if any(w in text for w in ["sad", "cry", "crying", "unhappy", "hurts"]):
        return "sad"
    if any(w in text for w in ["tired", "sleepy", "yawn", "nap"]):
        return "sleepy"
    if any(w in text for w in ["haha", "silly", "funny", "rawr"]):
        return "silly"
    if any(w in text for w in ["why", "what", "how", "look"]):
        return "curious"

    return selected_mood if selected_mood in ["happy", "curious", "silly", "sleepy"] else "happy"
