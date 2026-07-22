"""Unit tests for markdown_formatter module."""

import pytest
from src.markdown_formatter import MarkdownFormatter, MarkdownFormatError

SAMPLE_VALID_MARKDOWN = """# Day 001: Introduction to Python

## 🎯 Learning Objectives
- Learn Python history
- Write Hello World

## 📚 Theory & Concepts
Python is an interpreted, high-level programming language.

## 💻 Syntax & Structure
```python
print("Hello World")
```

## 🧪 Code Examples
```python
name = "Python"
print(f"Welcome to {name}")
```

## 📊 Expected Output
```text
Welcome to Python
```

## 🌍 Real-World Applications
Used in web dev, data science, and AI.

## 💡 Best Practices
- Follow PEP 8 guidelines.

## 📝 Summary & Key Takeaways
Python is simple and readable.
"""


def test_sanitize_raw_markdown():
    raw = "```markdown\n# Header\nContent\n```"
    sanitized = MarkdownFormatter.sanitize_raw_markdown(raw)
    assert sanitized == "# Header\nContent"


def test_validate_valid_markdown():
    is_valid, missing = MarkdownFormatter.validate_sections(SAMPLE_VALID_MARKDOWN)
    assert is_valid is True
    assert len(missing) == 0


def test_missing_sections_detection():
    invalid_md = "# Day 001: Intro\n\n## Theory\nSome theory here."
    is_valid, missing = MarkdownFormatter.validate_sections(invalid_md)
    assert is_valid is False
    assert "Learning Objectives" in missing
    assert "Expected Output" in missing


def test_format_lesson_success():
    formatted = MarkdownFormatter.format_lesson(SAMPLE_VALID_MARKDOWN, 1, "Intro")
    assert formatted.startswith("# Day 001:")
    assert formatted.endswith("\n")
