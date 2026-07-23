"""Target repository README dashboard generator for Codewithpython."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.progress_manager import ProgressState
from src.syllabus_manager import SyllabusManager, LessonMetadata


class ReadmeGenerator:
    """Generates dynamic README.md dashboard for target Codewithpython repository."""

    @staticmethod
    def render_progress_bar(completed: int, total: int = 90, bar_length: int = 15) -> str:
        """
        Renders a visually attractive, vibrant green progress bar using native green emoji blocks.
        """
        percentage = round((completed / total) * 100) if total > 0 else 0
        if completed > 0:
            filled_length = max(1, int(round(bar_length * completed / float(total))))
        else:
            filled_length = 0
            
        filled_length = min(filled_length, bar_length)
        unfilled_length = bar_length - filled_length
        
        # 🟩 = Green Square, ⬜ = Light Square
        bar = "🟩" * filled_length + "⬜" * unfilled_length
        return f"{bar} **{percentage}%** ({completed}/{total} Days)"

    @classmethod
    def generate_readme(
        cls,
        state: ProgressState,
        syllabus_mgr: SyllabusManager
    ) -> str:
        """
        Generates full README.md markdown text for target repository.
        """
        total_days = syllabus_mgr.get_total_days()
        completed = state.last_published_lesson
        progress_bar = cls.render_progress_bar(completed, total_days)

        latest_lesson_link = "None (Course starts on Day 1)"
        if completed >= 1:
            try:
                latest_meta = syllabus_mgr.get_lesson(completed)
                filename = f"Day{completed:03d}_{latest_meta.title.replace(' ', '_').replace('/', '_')}.md"
                latest_lesson_link = f"[Day {completed:03d}: {latest_meta.title}]({filename})"
            except Exception:
                latest_lesson_link = f"Day {completed:03d}"

        next_lesson_str = "Course Complete! 🎉"
        if state.next_lesson <= total_days:
            try:
                next_meta = syllabus_mgr.get_lesson(state.next_lesson)
                next_lesson_str = f"Day {state.next_lesson:03d}: {next_meta.title}"
            except Exception:
                next_lesson_str = f"Day {state.next_lesson:03d}"

        raw_updated = state.last_successful_publish
        if raw_updated:
            try:
                dt = datetime.fromisoformat(raw_updated)
                last_updated = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                last_updated = raw_updated
        else:
            last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Generate Table of Contents for published lessons
        toc_rows = []
        for d in range(1, completed + 1):
            try:
                meta = syllabus_mgr.get_lesson(d)
                filename = f"Day{d:03d}_{meta.title.replace(' ', '_').replace('/', '_')}.md"
                toc_rows.append(
                    f"| Day {d:03d} | [{meta.title}]({filename}) | `{meta.topic}` | {meta.difficulty} |"
                )
            except Exception:
                continue

        toc_section = ""
        if toc_rows:
            toc_section = "\n".join(toc_rows)
        else:
            toc_section = "| - | No lessons published yet. | - | - |"

        markdown = f"""# Python 90 Days Mastery Course 🐍

Welcome to **Codewithpython** -- a structured, beginner-to-intermediate Python curriculum published automatically every single day!

---

## 📊 Course Dashboard

- **Overall Progress**: {progress_bar}
- **Current Streak**: 🔥 **{state.current_streak} Days**
- **Latest Published Lesson**: 📖 {latest_lesson_link}
- **Up Next**: 🔜 **{next_lesson_str}**
- **Last Updated**: 🕒 `{last_updated}`

---

## 📚 Curriculum Table of Contents

| Day | Lesson Title | Topic | Difficulty |
| :---: | :--- | :---: | :---: |
{toc_section}

---

## 🤖 Automation & System Info

> **Notice**: This repository is automatically maintained and populated by **[GitHubDev](https://github.com/deepakrajjs-29/GitHubDev)** -- an unattended Python automation engine powered by **GitHub Actions** and **Google Gemini API**.
"""
        return markdown.strip() + "\n"
