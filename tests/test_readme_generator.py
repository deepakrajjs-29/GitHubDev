"""Unit tests for readme_generator module."""

import pytest
from src.readme_generator import ReadmeGenerator
from src.progress_manager import ProgressState
from src.syllabus_manager import SyllabusManager


def test_render_progress_bar():
    bar0 = ReadmeGenerator.render_progress_bar(0, 90)
    assert "0%" in bar0
    
    bar45 = ReadmeGenerator.render_progress_bar(45, 90)
    assert "50%" in bar45
    
    bar90 = ReadmeGenerator.render_progress_bar(90, 90)
    assert "100%" in bar90


def test_generate_readme_structure():
    state = ProgressState(last_published_lesson=1, next_lesson=2, current_streak=1)
    syllabus_mgr = SyllabusManager(syllabus_path="syllabus/python_90_days.json")
    
    readme_text = ReadmeGenerator.generate_readme(state, syllabus_mgr)
    assert "# Python 90 Days Mastery Course" in readme_text
    assert "Course Dashboard" in readme_text
    assert "GitHubDev" in readme_text
    assert "Day 001" in readme_text
