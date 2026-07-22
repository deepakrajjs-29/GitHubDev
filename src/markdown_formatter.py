"""Markdown formatting, validation, and sanitization module for GitHubDev engine."""

import re
from typing import List, Dict, Tuple


class MarkdownFormatError(Exception):
    """Raised when generated lesson markdown fails structure or section validation."""
    pass


REQUIRED_SECTION_KEYWORDS: Dict[str, List[str]] = {
    "Title": ["# day"],
    "Learning Objectives": ["objective"],
    "Theory": ["theory", "concept"],
    "Syntax": ["syntax", "structure"],
    "Code Examples": ["example"],
    "Expected Output": ["output"],
    "Real-World Applications": ["real-world", "application", "use case"],
    "Best Practices": ["best practice", "pitfall", "tip"],
    "Summary": ["summary", "takeaway"]
}


class MarkdownFormatter:
    """Sanitizes, formats, and validates Gemini markdown output."""

    @staticmethod
    def sanitize_raw_markdown(raw_text: str) -> str:
        """Removes code fence meta-wrappers if Gemini wraps response in markdown block."""
        text = raw_text.strip()
        
        # Remove opening ```markdown or ``` wrapper
        text = re.sub(r"^```(?:markdown|md)?\n", "", text, flags=re.IGNORECASE)
        # Remove trailing ```
        text = re.sub(r"\n```$", "", text)
        
        return text.strip()

    @classmethod
    def validate_sections(cls, markdown_text: str) -> Tuple[bool, List[str]]:
        """
        Validates presence of all 9 required sections in lesson markdown.
        
        Returns:
            Tuple of (is_valid, list_of_missing_sections)
        """
        sanitized = cls.sanitize_raw_markdown(markdown_text)
        lower_text = sanitized.lower()
        missing_sections = []

        for section_name, keywords in REQUIRED_SECTION_KEYWORDS.items():
            found = any(kw.lower() in lower_text for kw in keywords)
            if not found:
                missing_sections.append(section_name)

        return len(missing_sections) == 0, missing_sections

    @classmethod
    def format_lesson(cls, raw_markdown: str, lesson_number: int, lesson_title: str) -> str:
        """
        Sanitizes and enforces standard layout spacing for lesson markdown.
        
        Raises:
            MarkdownFormatError if required sections are missing.
        """
        sanitized = cls.sanitize_raw_markdown(raw_markdown)
        is_valid, missing = cls.validate_sections(sanitized)
        
        if not is_valid:
            raise MarkdownFormatError(
                f"Generated lesson for Day {lesson_number} missing required sections: {', '.join(missing)}"
            )

        # Standardize heading spacing
        formatted = re.sub(r"\n{3,}", "\n\n", sanitized)
        return formatted.strip() + "\n"
