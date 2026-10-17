import time
import logging
import re
from typing import List, Dict, Optional, Tuple
import httpx
from app.config import get_settings

logger = logging.getLogger("ai_service")
settings = get_settings()

# Fallback models in priority order if primary model is rate-limited upstream
FALLBACK_MODELS = [
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3.5-lightning:free"
]

# Domain-aware dynamic pedagogical responses when upstream LLM is rate-limited
DYNAMIC_PEDAGOGICAL_PATTERNS = [
    (r"\b(apple|apples)\b", "Yum! Apples are crunchy and sweet! 🍎 Can you say 'Red Apple'?"),
    (r"\b(cat|cats|kitten)\b", "Meow! Cats are soft and cuddly! 🐱 Can you say 'Cat'?"),
    (r"\b(dog|dogs|puppy)\b", "Woof woof! Dogs love to run and play! 🐶 Can you say 'Happy Dog'?"),
    (r"\b(sun|sunny)\b", "The sun is bright and warm! ☀️ Can you say 'Bright Sun'?"),
    (r"\b(ball|balls)\b", "Bounce bounce! Let's kick the big ball! ⚽ Can you say 'Big Ball'?"),
    (r"\b(car|cars|truck)\b", "Vroom vroom! The fast red car zooms by! 🚗 Can you say 'Fast Car'?"),
    (r"\b(bird|birds)\b", "Chirp chirp! The little bird flies high in the sky! 🐦 Can you say 'Little Bird'?"),
    (r"\b(cow|cows)\b", "Moo moo! The black and white cow eats green grass! 🐮 Can you say 'Moo'?"),
]

OFFLINE_LEVEL_FALLBACKS = {
    "L1": "You are doing wonderful! 🌟 Say: 'A is for Apple!' 🍎",
    "L2": "Great job, explorer! ⭐ The bird flies up high! 🐦 What color is the bird?",
    "L3": "Super storytelling! 🚀 The puppy found a secret garden. Should we look inside? 🐶"
}
OFFLINE_PEDAGOGICAL_FALLBACKS = OFFLINE_LEVEL_FALLBACKS



def build_system_prompt(
    current_level: str = "L1",
    current_mode: str = "learning",
    selected_mood: str = "happy"
) -> str:
    """
    Constructs an age-appropriate system prompt for early childhood (under 7).
    Enforces strict brevity (<30 words), positive reinforcement, and level guidance.
    """
    level_guidelines = {
        "L1": (
            "Target: Ages 3-4 (Seedling). Focus on single words, phonics sounds (e.g. 'B says buh!'), "
            "animal noises, and basic colors/fruits. Use 1 short sentence only. Ask child to repeat a word."
        ),
        "L2": (
            "Target: Ages 4-5 (Explorer). Focus on 2-3 word phrases, counting 1-10, colors, and simple actions "
            "(e.g. 'The bird flies!'). Use 1-2 short sentences. Ask child to complete a phrase."
        ),
        "L3": (
            "Target: Ages 6-7 (Storyteller). Focus on simple full sentences, mini-stories, and friendly 'Why/What' "
            "questions. Use 2 short sentences. Offer a fun choice."
        )
    }

    mode_guidelines = {
        "learning": "Structured bite-sized English lesson. Celebrate, teach 1 word/phrase, and prompt child.",
        "conversation": "Casual friendly companion chat. Ask about their favorite toy, animal, or game.",
        "engagement": "Playful game, animal sound imitation, silly joke, or rhyme to recapture attention.",
        "support": "Comforting, calm, soothing reassurance. No testing. Remind child that learning is fun and mistakes are welcome."
    }

    selected_level_guide = level_guidelines.get(current_level, level_guidelines["L1"])
    selected_mode_guide = mode_guidelines.get(current_mode, mode_guidelines["learning"])

    return (
        "You are 'Buddy', a gentle, cheerful English learning companion for young children under 7 years old.\n"
        f"Child's Current Level: {current_level}. {selected_level_guide}\n"
        f"Interaction Mode: {current_mode}. {selected_mode_guide}\n"
        f"Child's Selected Mood: {selected_mood}. Respond with matching warmth and empathy.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. Length: MAXIMUM 20-30 words (1 to 2 short sentences). Pre-literate children lose focus quickly.\n"
        "2. Tone: Warm, energetic, playful, and loving. Always include 1-2 friendly emojis (🐶, 🌟, 🍎, 🎈).\n"
        "3. SEL Positive Reinforcement: NEVER say 'No', 'Wrong', or 'Incorrect'. If child makes an error, "
        "praise their attempt ('Good try!', 'High five!') and gently model the word.\n"
        "4. Output format: Return ONLY the spoken response. No meta-commentary, no markdown headers."
    )


async def call_openrouter_api(
    model: str,
    messages: List[Dict[str, str]],
    timeout_seconds: float = 1.0
) -> Optional[str]:
    """
    Asynchronously calls the OpenRouter chat completions API with token bounding and strict timeout.
    """
    if not settings.OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://english-learning-chatbot.local",
        "X-Title": "English Learning Chatbot for Children"
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 50,
        "temperature": 0.6
    }

    url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return None
                message_obj = choices[0].get("message", {})
                content = message_obj.get("content")
                if not content and message_obj.get("reasoning"):
                    content = message_obj.get("reasoning")
                if content:
                    clean = content.strip()
                    if (clean.startswith('"') and clean.endswith('"')) or (clean.startswith("'") and clean.endswith("'")):
                        clean = clean[1:-1].strip()
                    return clean
                return None
            else:
                logger.warning(f"OpenRouter model {model} returned HTTP {response.status_code}")
                return None
    except Exception as e:
        logger.warning(f"OpenRouter call failed for {model}: {e}")
        return None


def get_smart_pedagogical_fallback(user_message: str, current_level: str) -> str:
    """
    Provides an intelligent, instant (<2ms) pedagogical response matching
    the child's message content if upstream LLMs are unavailable or rate-limited.
    """
    text = (user_message or "").lower()
    for pattern, reply in DYNAMIC_PEDAGOGICAL_PATTERNS:
        if re.search(pattern, text):
            return reply
    return OFFLINE_LEVEL_FALLBACKS.get(current_level, OFFLINE_LEVEL_FALLBACKS["L1"])


async def generate_child_ai_response(
    user_message: str,
    current_level: str = "L1",
    current_mode: str = "learning",
    selected_mood: str = "happy",
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_budget_seconds: float = 0.8
) -> Tuple[str, int]:
    """
    Main orchestration function to generate a child-safe AI response.
    Enforces a strict total budget to guarantee the <2.0s SLA requirement.
    Returns: (reply_text, latency_ms)
    """
    start_time = time.perf_counter()
    GLOBAL_BUDGET_SECONDS = max(0.3, max_budget_seconds)

    # 1. Build messages payload
    system_prompt = build_system_prompt(current_level, current_mode, selected_mood)
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        for turn in conversation_history[-4:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    clean_input = user_message.strip() if user_message else "Hello!"
    messages.append({"role": "user", "content": clean_input})

    # 2. Try primary model with remaining budget
    reply = None
    elapsed = time.perf_counter() - start_time
    remaining = GLOBAL_BUDGET_SECONDS - elapsed

    if remaining > 0.3:
        reply = await call_openrouter_api(settings.OPENROUTER_MODEL, messages, timeout_seconds=min(0.7, remaining))

    # 3. Try quick fallback model if budget permits
    if not reply:
        for fallback_model in FALLBACK_MODELS:
            elapsed = time.perf_counter() - start_time
            remaining = GLOBAL_BUDGET_SECONDS - elapsed
            if remaining <= 0.2:
                break
            reply = await call_openrouter_api(fallback_model, messages, timeout_seconds=min(0.4, remaining))
            if reply:
                break

    # 4. If all remote calls failed or budget expired, use instant smart pedagogical fallback
    if not reply:
        reply = get_smart_pedagogical_fallback(clean_input, current_level)

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    return reply, latency_ms
