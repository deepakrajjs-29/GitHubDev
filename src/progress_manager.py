"""Progress and state management module for GitHubDev automation engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError


class ProgressState(BaseModel):
    """Pydantic model representing persistent state in progress.json."""
    current_lesson_number: int = Field(default=0, ge=0)
    current_lesson_title: str = Field(default="")
    last_published_lesson: int = Field(default=0, ge=0)
    next_lesson: int = Field(default=1, ge=1)
    total_published_lessons: int = Field(default=0, ge=0)
    current_streak: int = Field(default=0, ge=0)
    last_successful_publish: Optional[str] = None
    last_successful_api_call: Optional[str] = None
    cached_until: Optional[str] = None
    last_cache_generation: Optional[str] = None
    current_course: str = Field(default="Python 90 Days Mastery")
    course_duration: int = Field(default=90, ge=1)
    system_version: str = Field(default="1.0.0")
    publishing_status: str = Field(default="IDLE")
    recovery_required: bool = Field(default=False)
    pending_lesson: Optional[int] = None


class StateError(Exception):
    """Raised when reading, writing, or validating state/progress.json fails."""
    pass


def load_progress(file_path: str = "state/progress.json", base_dir: Optional[Path] = None) -> ProgressState:
    """
    Reads and validates progress state from JSON.
    
    Args:
        file_path: Path to progress.json
        base_dir: Optional base path resolution
        
    Returns:
        ProgressState instance
    """
    if base_dir is None:
        base_dir = Path.cwd()
        
    full_path = Path(file_path)
    if not full_path.is_absolute():
        full_path = base_dir / file_path

    if not full_path.exists():
        # Initialize default state file if absent
        default_state = ProgressState()
        save_progress(default_state, str(full_path))
        return default_state

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        return ProgressState(**raw_data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise StateError(f"Failed to parse or validate progress state from {full_path}: {exc}") from exc


def save_progress(state: ProgressState, file_path: str = "state/progress.json", base_dir: Optional[Path] = None) -> None:
    """
    Saves progress state atomically to JSON.
    
    Args:
        state: ProgressState instance to save
        file_path: Target progress.json file path
        base_dir: Optional base path resolution
    """
    if base_dir is None:
        base_dir = Path.cwd()
        
    full_path = Path(file_path)
    if not full_path.is_absolute():
        full_path = base_dir / file_path

    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first for atomic overwrite safety
    temp_path = full_path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2)
        temp_path.replace(full_path)
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise StateError(f"Failed to write progress state to {full_path}: {exc}") from exc


def update_progress_after_publish(
    lesson_number: int,
    lesson_title: str,
    file_path: str = "state/progress.json",
    base_dir: Optional[Path] = None
) -> ProgressState:
    """
    Updates and persists progress state ONLY AFTER successful publication.
    
    Args:
        lesson_number: Published lesson day number
        lesson_title: Published lesson title
        file_path: Path to progress.json
        base_dir: Base directory
        
    Returns:
        Updated ProgressState instance
    """
    state = load_progress(file_path, base_dir)
    now_iso = datetime.now(timezone.utc).isoformat()
    
    state.current_lesson_number = lesson_number
    state.current_lesson_title = lesson_title
    state.last_published_lesson = lesson_number
    state.next_lesson = lesson_number + 1
    state.total_published_lessons += 1
    state.current_streak += 1
    state.last_successful_publish = now_iso
    state.publishing_status = "IDLE"
    state.recovery_required = False
    state.pending_lesson = None
    
    save_progress(state, file_path, base_dir)
    return state


def flag_recovery_needed(
    lesson_number: int,
    file_path: str = "state/progress.json",
    base_dir: Optional[Path] = None
) -> ProgressState:
    """
    Flags that a lesson publishing failed and requires recovery without incrementing progress.
    
    Args:
        lesson_number: Failed lesson number
        file_path: Path to progress.json
        base_dir: Base directory
        
    Returns:
        Updated ProgressState instance
    """
    state = load_progress(file_path, base_dir)
    state.publishing_status = "FAILED"
    state.recovery_required = True
    state.pending_lesson = lesson_number
    save_progress(state, file_path, base_dir)
    return state
