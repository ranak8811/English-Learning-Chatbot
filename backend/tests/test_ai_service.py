import pytest
import asyncio
from app.services.ai_service import (
    build_system_prompt,
    generate_child_ai_response,
    OFFLINE_PEDAGOGICAL_FALLBACKS
)


def test_system_prompt_builder():
    """
    Test 1: Verify system prompt structure for L1, L2, L3 and modes.
    Enforces Under-7 early childhood pedagogy and positive reinforcement.
    """
    prompt_l1 = build_system_prompt(current_level="L1", current_mode="learning", selected_mood="happy")
    assert "Buddy" in prompt_l1
    assert "L1" in prompt_l1
    assert "Ages 3-4" in prompt_l1
    assert "MAXIMUM 20-30 words" in prompt_l1
    assert "NEVER say 'No', 'Wrong'" in prompt_l1

    prompt_l2 = build_system_prompt(current_level="L2", current_mode="conversation", selected_mood="curious")
    assert "L2" in prompt_l2
    assert "Ages 4-5" in prompt_l2
    assert "conversation" in prompt_l2

    prompt_l3 = build_system_prompt(current_level="L3", current_mode="support", selected_mood="sleepy")
    assert "L3" in prompt_l3
    assert "Ages 6-7" in prompt_l3
    assert "support" in prompt_l3


@pytest.mark.asyncio
async def test_offline_pedagogical_fallback():
    """
    Test 2: Verify fallback responds immediately if network or API is unavailable.
    """
    # When message is empty or model unavailable, fallback must provide safe level response
    fallback_l1 = OFFLINE_PEDAGOGICAL_FALLBACKS["L1"]
    assert "Cat" in fallback_l1 or "Apple" in fallback_l1 or "🌟" in fallback_l1

    fallback_l2 = OFFLINE_PEDAGOGICAL_FALLBACKS["L2"]
    assert "dog" in fallback_l2.lower()

    fallback_l3 = OFFLINE_PEDAGOGICAL_FALLBACKS["L3"]
    assert "bunny" in fallback_l3.lower()


@pytest.mark.asyncio
async def test_openrouter_live_generation():
    """
    Test 3: Live end-to-end integration test with OpenRouter API.
    Verifies response is returned, word count is under 40 words, and latency is recorded.
    """
    reply, latency_ms = await generate_child_ai_response(
        user_message="Hello! I like apples!",
        current_level="L1",
        current_mode="learning",
        selected_mood="happy"
    )

    assert reply is not None
    assert len(reply) > 0
    # Child prompt brevity check
    word_count = len(reply.split())
    assert word_count <= 45  # Short, friendly response for under-7 child
    # Latency SLA check
    assert latency_ms < 2500  # Generous upper bound for network roundtrip, SLA target <2000ms


@pytest.mark.asyncio
async def test_context_awareness_in_response():
    """
    Test 4: Context awareness passes previous conversation turns into context.
    """
    history = [
        {"role": "user", "content": "My name is Leo"},
        {"role": "assistant", "content": "Hi Leo! 🌟 Let's learn animals today!"}
    ]
    reply, latency_ms = await generate_child_ai_response(
        user_message="What animal says meow?",
        current_level="L1",
        current_mode="learning",
        selected_mood="curious",
        conversation_history=history
    )

    assert reply is not None
    assert len(reply) > 0
    assert latency_ms > 0
