"""Unit tests for publisher module."""

import pytest
from unittest.mock import MagicMock, patch
from src.publisher import Publisher


def test_publisher_dry_run(tmp_path):
    progress_file = (tmp_path / "progress.json").as_posix()
    cache_dir = (tmp_path / "cache").as_posix()
    log_file = (tmp_path / "automation_log.md").as_posix()
    
    config_content = f"""
project:
  name: "Test"
state:
  file_path: "{progress_file}"
syllabus:
  file_path: "syllabus/python_90_days.json"
prompt:
  template_path: "prompts/python_lesson_prompt.md"
cache:
  cache_directory: "{cache_dir}"
logging:
  automation_log_file: "{log_file}"
gemini:
  primary_model: "gemini-2.5-flash"
  retry_count: 1
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    
    with patch("src.publisher.GeminiClient") as mock_gemini_cls:
        mock_client = MagicMock()
        mock_client.generate_lesson_markdown.return_value = {
            "content": """# Day 001: Introduction to Python & Setup

## 🎯 Learning Objectives
- Obj 1

## 📚 Theory & Concepts
Theory

## 💻 Syntax & Structure
```python
code
```

## 🧪 Code Examples
```python
example
```

## 📊 Expected Output
```text
out
```

## 🌍 Real-World Applications
App

## 💡 Best Practices
- Best practice

## 📝 Summary & Key Takeaways
Summary
""",
            "model_used": "gemini-2.5-flash"
        }
        mock_gemini_cls.return_value = mock_client
        
        publisher = Publisher(config_path=str(config_file))
        publisher._gemini_client = mock_client
        
        success = publisher.run_daily_publish(force_day=1, dry_run=True)
        assert success is True
