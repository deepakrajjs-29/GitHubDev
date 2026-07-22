"""Unit tests for prompt_builder module."""

import pytest
from pathlib import Path
from src.prompt_builder import PromptBuilder, PromptError
from src.syllabus_manager import LessonMetadata


def test_build_valid_prompt():
    builder = PromptBuilder(template_path="prompts/python_lesson_prompt.md")
    lesson = LessonMetadata(
        day=1,
        title="Introduction to Python & Setup",
        topic="Fundamentals",
        difficulty="Beginner",
        reading_time="10 mins",
        prerequisites="None",
        objectives=["Install Python"]
    )
    
    prompt = builder.build_prompt(lesson=lesson, course_name="Python 90 Days Mastery")
    assert "Day 1" in prompt
    assert "Introduction to Python & Setup" in prompt
    assert "Fundamentals" in prompt
    assert "Beginner" in prompt


def test_nonexistent_prompt_template():
    with pytest.raises(PromptError, match="not found"):
        PromptBuilder(template_path="prompts/invalid_prompt_name.md")
