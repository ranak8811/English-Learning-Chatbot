from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.child import (
    ChildCreateRequest,
    ChildProfileResponse,
    MoodRecordRequest,
    TurnHistoryResponse
)
from app.services.db_service import (
    get_child_profile,
    get_or_create_child_profile,
    record_sel_mood,
    get_mastered_words,
    get_recent_turns
)

router = APIRouter(prefix="/api/child", tags=["Child Profile"])


@router.post("", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_or_initialize_child(
    request: ChildCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Creates a new child learner profile or retrieves existing profile.
    """
    profile = get_or_create_child_profile(
        db=db,
        name=request.name,
        age=request.age,
        level=request.current_level
    )
    mastered = get_mastered_words(db, profile.id)

    return ChildProfileResponse(
        id=profile.id,
        name=profile.name,
        age=profile.age,
        current_level=profile.current_level,
        current_mode=profile.current_mode,
        stars_earned=profile.stars_earned,
        mastered_words=mastered,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.get("/{child_id}", response_model=ChildProfileResponse)
def get_child_details(
    child_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves full progress profile for a child including mastered words.
    """
    profile = get_child_profile(db, child_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found."
        )
    mastered = get_mastered_words(db, profile.id)

    return ChildProfileResponse(
        id=profile.id,
        name=profile.name,
        age=profile.age,
        current_level=profile.current_level,
        current_mode=profile.current_mode,
        stars_earned=profile.stars_earned,
        mastered_words=mastered,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.post("/{child_id}/mood")
def record_child_mood(
    child_id: UUID,
    request: MoodRecordRequest,
    db: Session = Depends(get_db)
):
    """
    Records an SEL emotional check-in event (happy, curious, silly, sleepy).
    """
    profile = get_child_profile(db, child_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found.")

    mood_log = record_sel_mood(db, child_id, request.mood)
    return {
        "status": "success",
        "child_id": child_id,
        "mood_recorded": mood_log.mood_selected,
        "logged_at": mood_log.logged_at
    }


@router.get("/{child_id}/history", response_model=List[TurnHistoryResponse])
def get_child_history(
    child_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieves recent conversational turn history for session playback.
    """
    profile = get_child_profile(db, child_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found.")

    turns = get_recent_turns(db, child_id, limit=limit)
    return turns
