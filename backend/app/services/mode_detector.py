import re
from typing import Optional


SUPPORT_KEYWORDS = [
    "tired", "sleepy", "exhausted", "sleep", "nap", "bed",
    "hard", "too hard", "difficult", "i can't", "cant", "cannot",
    "dont know", "don't know", "i dont know", "confused", "stuck",
    "sad", "cry", "crying", "unhappy", "angry", "mad", "hate",
    "stop", "no more", "want to stop", "want mommy", "want daddy"
]

ENGAGEMENT_KEYWORDS = [
    "haha", "hehe", "lol", "silly", "funny", "joke", "tickle",
    "rawr", "grrr", "roar", "meow", "woof", "quack", "oink", "moo",
    "beep", "boop", "vroom", "zoom", "ding", "dinosaur", "monster",
    "boring", "play a game", "tell a joke", "sing", "dance"
]

CONVERSATION_KEYWORDS = [
    "my name is", "i am", "i'm", "i like", "i love", "my favorite",
    "i have", "look at my", "today i", "yesterday", "my friend",
    "my dog", "my cat", "my mom", "my dad", "how are you", "what is your name",
    "who are you", "do you like", "good morning", "good night"
]


def detect_child_mode(
    message: str,
    selected_mood: str = "happy",
    current_mode: str = "learning"
) -> str:
    """
    Detects the child's interaction mode based on utterance, mood, and context.
    Evaluates in priority order:
    1. Support Mode (Fatigue, sadness, frustration, requests to stop)
    2. Engagement Mode (Silly noises, playful games, animal sounds, boredom)
    3. Conversation Mode (Casual chatting, sharing about personal life)
    4. Learning Mode (Pedagogical answers, vocabulary practice, default)
    """
    text = (message or "").strip().lower()

    if not text:
        return "support" if selected_mood == "sleepy" else current_mode

    # 1. Check for Support Mode triggers (Highest Priority: Child Emotional Wellbeing)
    for kw in SUPPORT_KEYWORDS:
        if kw in text:
            return "support"

    # If child explicitly set mood to 'sleepy' and message is short/low energy
    if selected_mood == "sleepy" and len(text.split()) <= 2:
        return "support"

    # 2. Check for Engagement Mode triggers (Playful/Silly/Bored)
    for kw in ENGAGEMENT_KEYWORDS:
        if kw in text:
            return "engagement"

    # Single character repetitions like "aaaa", "zzzz", "hahaha"
    if re.search(r"(.)\1{3,}", text) or "haha" in text:
        return "engagement"

    if selected_mood == "silly" and (len(text.split()) <= 2 or "!" in text):
        return "engagement"

    # 3. Check for Conversation Mode triggers (Casual buddy chat)
    for kw in CONVERSATION_KEYWORDS:
        if kw in text:
            return "conversation"

    # If child asks a question ("what is that?", "why is the sky blue?")
    if text.endswith("?") or text.startswith(("why", "what", "where", "who", "when")):
        return "conversation"

    # 4. Default to Learning Mode for lesson-related answers and practice
    return "learning"
