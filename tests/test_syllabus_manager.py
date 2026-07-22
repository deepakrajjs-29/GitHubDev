"""Unit tests for syllabus_manager module."""

import pytest
from pathlib import Path
from src.syllabus_manager import SyllabusManager, SyllabusError, LessonMetadata


def test_load_valid_syllabus():
    manager = SyllabusManager(syllabus_path="syllabus/python_90_days.json")
    assert manager.get_total_days() == 90
    
    lesson1 = manager.get_lesson(1)
    assert isinstance(lesson1, LessonMetadata)
    assert lesson1.day == 1
    assert lesson1.title == "Introduction to Python & Setup"
    assert lesson1.difficulty == "Beginner"


def test_get_out_of_bounds_lesson():
    manager = SyllabusManager(syllabus_path="syllabus/python_90_days.json")
    with pytest.raises(SyllabusError, match="not found in syllabus"):
        manager.get_lesson(999)


def test_get_previous_history_summary():
    manager = SyllabusManager(syllabus_path="syllabus/python_90_days.json")
    summary_day1 = manager.get_previous_lessons_summary(1)
    assert summary_day1 == "None (First lesson of the course)"
    
    summary_day4 = manager.get_previous_lessons_summary(4)
    assert "Day 1:" in summary_day4
    assert "Day 2:" in summary_day4
    assert "Day 3:" in summary_day4
