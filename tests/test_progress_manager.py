"""Unit tests for progress_manager module."""

import pytest
from pathlib import Path
from src.progress_manager import (
    load_progress,
    save_progress,
    update_progress_after_publish,
    flag_recovery_needed,
    ProgressState,
    StateError
)


def test_load_default_progress(tmp_path):
    progress_file = tmp_path / "progress.json"
    state = load_progress(str(progress_file))
    assert state.current_lesson_number == 0
    assert state.next_lesson == 1
    assert state.recovery_required is False


def test_update_progress_after_publish(tmp_path):
    progress_file = tmp_path / "progress.json"
    updated_state = update_progress_after_publish(
        lesson_number=1,
        lesson_title="Introduction to Python & Setup",
        file_path=str(progress_file)
    )
    assert updated_state.current_lesson_number == 1
    assert updated_state.last_published_lesson == 1
    assert updated_state.next_lesson == 2
    assert updated_state.total_published_lessons == 1
    assert updated_state.current_streak == 1
    assert updated_state.last_successful_publish is not None


def test_flag_recovery_needed(tmp_path):
    progress_file = tmp_path / "progress.json"
    state = flag_recovery_needed(lesson_number=2, file_path=str(progress_file))
    assert state.publishing_status == "FAILED"
    assert state.recovery_required is True
    assert state.pending_lesson == 2
    # Progress number must stay unchanged
    assert state.current_lesson_number == 0
