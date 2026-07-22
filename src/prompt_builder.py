"""Prompt template builder module for GitHubDev engine."""

from pathlib import Path
from typing import Optional, Dict, Any
from src.syllabus_manager import LessonMetadata


class PromptError(Exception):
    """Raised when prompt reading or formatting fails."""
    pass


class PromptBuilder:
    """Loads prompt markdown template and formats variables for Gemini API request."""
    
    def __init__(self, template_path: str = "prompts/python_lesson_prompt.md", base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.cwd()
            
        full_path = Path(template_path)
        if not full_path.is_absolute():
            full_path = base_dir / template_path
            
        self.full_path = full_path
        self.template_text: str = self._load_template()

    def _load_template(self) -> str:
        if not self.full_path.exists():
            raise PromptError(f"Prompt template file not found at: {self.full_path}")
            
        try:
            with open(self.full_path, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                raise PromptError(f"Prompt template file at {self.full_path} is empty.")
            return content
        except Exception as exc:
            raise PromptError(f"Failed to read prompt template: {exc}") from exc

    def build_prompt(
        self,
        lesson: LessonMetadata,
        course_name: str = "Python 90 Days Mastery",
        previous_lessons_summary: str = "None"
    ) -> str:
        """
        Populates template variables with lesson metadata.
        
        Args:
            lesson: LessonMetadata object from syllabus
            course_name: Name of the course
            previous_lessons_summary: History context string of recent lessons
            
        Returns:
            Fully compiled prompt string ready for Gemini API call
        """
        try:
            prompt = self.template_text.format(
                lesson_number=lesson.day,
                lesson_title=lesson.title,
                topic=lesson.topic,
                difficulty=lesson.difficulty,
                estimated_reading_time=lesson.reading_time,
                prerequisites=lesson.prerequisites,
                course_name=course_name,
                previous_lessons=previous_lessons_summary
            )
            return prompt
        except KeyError as exc:
            raise PromptError(f"Missing placeholder variable during prompt formatting: {exc}") from exc
