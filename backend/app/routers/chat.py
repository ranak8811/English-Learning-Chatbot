import time
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.db_service import (
    get_or_create_child_profile,
    get_child_profile,
    get_recent_turns,
    log_turn,
    add_star_and_check_progress,
    record_mastered_word
)
from app.services.mode_detector import detect_child_mode
from app.services.sel_engine import format_sel_reinforcement, detect_emotion
from app.services.learning_engine import evaluate_learning_step
from app.services.ai_service import generate_child_ai_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])


def persist_interaction_background(
    child_id: UUID,
    user_message: str,
    assistant_reply: str,
    detected_mode: str,
    detected_emotion: str,
    level: str,
    latency_ms: int,
    stars_to_award: int,
    mastered_word: str = None
):
    """
    Background worker task to persist turns and progress into Neon PostgreSQL.
    Detached from the critical HTTP request path to guarantee <2.0s SLA.
    """
    db = SessionLocal()
    try:
        # 1. Log User Turn
        log_turn(
            db=db,
            child_id=child_id,
            role="user",
            content=user_message,
            detected_mode=detected_mode,
            detected_emotion=detected_emotion,
            level=level,
            latency_ms=0
        )
        # 2. Log Assistant Turn
        log_turn(
            db=db,
            child_id=child_id,
            role="assistant",
            content=assistant_reply,
            detected_mode=detected_mode,
            detected_emotion=detected_emotion,
            level=level,
            latency_ms=latency_ms
        )
        # 3. Update Child Profile Mode and Level
        profile = get_child_profile(db, child_id)
        if profile:
            profile.current_mode = detected_mode
            profile.current_level = level
            db.commit()

        # 4. Award Stars if earned
        if stars_to_award > 0:
            add_star_and_check_progress(db, child_id, stars_to_add=stars_to_award)

        # 5. Record Mastered Vocabulary Word if applicable
        if mastered_word:
            record_mastered_word(db, child_id, mastered_word, level)
    finally:
        db.close()


@router.post("", response_model=ChatResponse)
async def chat_interaction(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Primary conversational endpoint for early childhood English learning.
    Orchestrates Mode Detection, Progressive Learning, Gemma-4 LLM, and SEL reinforcement.
    Response SLA: < 2.0s.
    """
    start_time = time.perf_counter()

    clean_message = request.message.strip()
    if not clean_message:
        clean_message = "Hello Buddy!"

    # 1. Resolve or create child profile
    if request.child_id:
        profile = get_child_profile(db, request.child_id)
        if not profile:
            profile = get_or_create_child_profile(db, name="Explorer", level=request.current_level or "L1")
    else:
        profile = get_or_create_child_profile(db, name="Explorer", level=request.current_level or "L1")

    # 2. Detect Child Mode (learning, conversation, engagement, support)
    active_mode = detect_child_mode(
        message=clean_message,
        selected_mood=request.selected_mood or "happy",
        current_mode=profile.current_mode
    )

    # 3. Progressive Learning Evaluation (L1, L2, L3 & Stars)
    effective_level, stars_to_award, level_up_rec, mastered_word = evaluate_learning_step(
        current_level=profile.current_level,
        stars_earned=profile.stars_earned,
        message=clean_message,
        mode=active_mode
    )

    # 4. Fetch recent conversation context (last 4 turns)
    recent_turns = get_recent_turns(db, profile.id, limit=4)
    history_context = [{"role": t.role, "content": t.content} for t in recent_turns]

    # 5. Generate Child-Safe AI Response via OpenRouter Gemma-4
    elapsed_so_far = time.perf_counter() - start_time
    remaining_budget = max(0.3, 1.5 - elapsed_so_far)

    raw_reply, _ = await generate_child_ai_response(
        user_message=clean_message,
        current_level=effective_level,
        current_mode=active_mode,
        selected_mood=request.selected_mood or "happy",
        conversation_history=history_context,
        max_budget_seconds=remaining_budget
    )

    # 6. Apply Social & Emotional Learning (SEL) Post-Processing
    final_reply = format_sel_reinforcement(
        reply=raw_reply,
        mode=active_mode,
        mood=request.selected_mood or "happy",
        awarded_star=(stars_to_award > 0)
    )

    # 7. Inferred Emotion
    detected_emotion = detect_emotion(clean_message, request.selected_mood or "happy")

    # 8. Compute total roundtrip latency
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    # 9. Enqueue DB write in background tasks to avoid blocking user response
    background_tasks.add_task(
        persist_interaction_background,
        child_id=profile.id,
        user_message=clean_message,
        assistant_reply=final_reply,
        detected_mode=active_mode,
        detected_emotion=detected_emotion,
        level=effective_level,
        latency_ms=elapsed_ms,
        stars_to_award=stars_to_award,
        mastered_word=mastered_word
    )

    return ChatResponse(
        reply=final_reply,
        child_id=profile.id,
        detected_mode=active_mode,
        detected_emotion=detected_emotion,
        level=effective_level,
        stars_awarded=stars_to_award,
        total_stars=profile.stars_earned + stars_to_award,
        level_up_recommended=level_up_rec,
        mastered_word=mastered_word,
        latency_ms=elapsed_ms
    )
