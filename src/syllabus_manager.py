"""Syllabus management and lookup module for GitHubDev engine."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ValidationError


class LessonMetadata(BaseModel):
    """Pydantic model representing a single lesson in the syllabus."""
    day: int = Field(ge=1)
    title: str
    topic: str
    difficulty: str
    reading_time: str
    prerequisites: str
    objectives: List[str] = Field(default_factory=list)


class SyllabusData(BaseModel):
    """Pydantic model representing the 90-day syllabus schema."""
    course_name: str
    version: str = Field(default="1.0.0")
    total_days: int = Field(default=90, ge=1)
    description: str = Field(default="")
    lessons: List[LessonMetadata]


class SyllabusError(Exception):
    """Raised when syllabus loading or validation fails."""
    pass


class SyllabusManager:
    """Manages course syllabus loading, lookup, and prerequisite validation."""
    
    def __init__(self, syllabus_path: str = "syllabus/python_90_days.json", base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.cwd()
            
        full_path = Path(syllabus_path)
        if not full_path.is_absolute():
            full_path = base_dir / syllabus_path
            
        self.full_path = full_path
        self.syllabus: SyllabusData = self._load_and_validate()
        self._lesson_map: Dict[int, LessonMetadata] = {
            lesson.day: lesson for lesson in self.syllabus.lessons
        }

    def _load_and_validate(self) -> SyllabusData:
        if not self.full_path.exists():
            raise SyllabusError(f"Syllabus file not found at: {self.full_path}")
            
        try:
            with open(self.full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            syllabus = SyllabusData(**data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise SyllabusError(f"Failed to parse syllabus JSON from {self.full_path}: {exc}") from exc

        # Verify contiguous lesson day numbering
        expected_day = 1
        for lesson in syllabus.lessons:
            if lesson.day != expected_day:
                raise SyllabusError(
                    f"Non-contiguous lesson day sequence in syllabus: expected Day {expected_day}, got Day {lesson.day}"
                )
            expected_day += 1

        return syllabus

    def get_lesson(self, day: int) -> LessonMetadata:
        """Retrieves lesson metadata for a specific day number."""
        if day not in self._lesson_map:
            raise SyllabusError(f"Lesson for Day {day} not found in syllabus (Total days: {self.syllabus.total_days})")
        return self._lesson_map[day]

    def get_total_days(self) -> int:
        """Returns the total duration in days of the syllabus course."""
        return self.syllabus.total_days

    def get_previous_lessons_summary(self, current_day: int, max_history: int = 3) -> str:
        """Returns a string summary of recently completed lessons as context for Gemini."""
        if current_day <= 1:
            return "None (First lesson of the course)"
            
        start_day = max(1, current_day - max_history)
        history_items = []
        for d in range(start_day, current_day):
            if d in self._lesson_map:
                history_items.append(f"Day {d}: {self._lesson_map[d].title}")
                
        return ", ".join(history_items) if history_items else "None"
