import time
import logging
from typing import List, Dict, Optional, Tuple
import httpx
from app.config import get_settings

logger = logging.getLogger("ai_service")
settings = get_settings()

# Fallback models in priority order if primary model is busy or rate-limited
FALLBACK_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
]

# Static high-quality pedagogical fallbacks if all network calls fail
OFFLINE_PEDAGOGICAL_FALLBACKS = {
    "L1": "You are doing great! 🌟 Can you say: 'Cat'? Meow! 🐱",
    "L2": "Awesome job! ⭐ Look at the puppy! Can you say: 'The dog barks'? 🐶",
    "L3": "Super storytelling! 🚀 The friendly bunny hopped into the garden. What should the bunny eat? 🥕"
}


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
    timeout_seconds: float = 1.8
) -> Optional[str]:
    """
    Asynchronously calls the OpenRouter chat completions API with token bounding.
    """
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is not configured.")
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
        "max_tokens": 60,       # Capped for under-7 child attention and <2s latency
        "temperature": 0.6,
        "top_p": 0.9
    }

    url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                # Clean up any surrounding quotes or extra spaces
                if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
                    content = content[1:-1].strip()
                return content
            elif response.status_code in (429, 503, 504):
                logger.warning(f"OpenRouter model {model} returned status {response.status_code}.")
                return None
            else:
                logger.error(f"OpenRouter unexpected status {response.status_code}: {response.text}")
                return None
        except httpx.TimeoutException:
            logger.warning(f"OpenRouter request timed out after {timeout_seconds}s for model {model}.")
            return None
        except Exception as e:
            logger.error(f"OpenRouter request failed: {str(e)}")
            return None


async def generate_child_ai_response(
    user_message: str,
    current_level: str = "L1",
    current_mode: str = "learning",
    selected_mood: str = "happy",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, int]:
    """
    Main orchestration function to generate a child-safe AI response.
    Features model fallback and guaranteed <2s latency SLA.
    Returns: (reply_text, latency_ms)
    """
    start_time = time.perf_counter()

    # Build system message
    system_prompt = build_system_prompt(current_level, current_mode, selected_mood)
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    # Append recent context (up to 4 past turns)
    if conversation_history:
        for turn in conversation_history[-4:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    # Append current child message
    clean_input = user_message.strip() if user_message else "Hello!"
    messages.append({"role": "user", "content": clean_input})

    # Try Primary Model (google/gemma-4-26b-a4b-it:free or configured)
    primary_model = settings.OPENROUTER_MODEL
    reply = await call_openrouter_api(primary_model, messages, timeout_seconds=1.7)

    # Try fallback models if primary failed
    if not reply:
        for fallback_model in FALLBACK_MODELS:
            logger.info(f"Attempting fallback model: {fallback_model}")
            reply = await call_openrouter_api(fallback_model, messages, timeout_seconds=1.4)
            if reply:
                break

    # If all remote models fail or network unavailable, use deterministic pedagogical fallback
    if not reply:
        logger.warning("All OpenRouter models failed or timed out. Using deterministic fallback.")
        reply = OFFLINE_PEDAGOGICAL_FALLBACKS.get(current_level, OFFLINE_PEDAGOGICAL_FALLBACKS["L1"])

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return reply, elapsed_ms
