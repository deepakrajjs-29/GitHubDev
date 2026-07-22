"""Main Publisher Orchestrator for GitHubDev engine."""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional

from src.config_loader import load_config, AppConfig
from src.logger import setup_logger
from src.progress_manager import (
    load_progress,
    save_progress,
    update_progress_after_publish,
    flag_recovery_needed,
    ProgressState
)
from src.syllabus_manager import SyllabusManager
from src.prompt_builder import PromptBuilder
from src.gemini_client import GeminiClient, GeminiError
from src.markdown_formatter import MarkdownFormatter, MarkdownFormatError
from src.cache_manager import CacheManager
from src.github_manager import GitHubManager
from src.readme_generator import ReadmeGenerator
from src.recovery_manager import RecoveryManager

logger = setup_logger()


class Publisher:
    """Orchestrates daily lesson publishing and Sunday batch cache generation."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config: AppConfig = load_config(config_path)
        self.syllabus_mgr = SyllabusManager(self.config.syllabus.file_path)
        self.prompt_builder = PromptBuilder(self.config.prompt.template_path)
        self.cache_mgr = CacheManager(self.config.cache.cache_directory)
        self.github_mgr = GitHubManager(self.config.repositories, self.config.github)
        self.recovery_mgr = RecoveryManager(self.config.logging.automation_log_file)
        
        # Lazy load Gemini Client to allow config without API key in mock tests
        self._gemini_client: Optional[GeminiClient] = None

    @property
    def gemini_client(self) -> GeminiClient:
        if self._gemini_client is None:
            self._gemini_client = GeminiClient(self.config.gemini)
        return self._gemini_client

    def run_daily_publish(self, force_day: Optional[int] = None, dry_run: bool = False) -> bool:
        """
        Executes daily publishing pipeline.
        
        Returns:
            True on successful publishing, False on failure.
        """
        state: ProgressState = load_progress(self.config.state.file_path)
        target_day = force_day if force_day is not None else state.next_lesson
        
        total_days = self.syllabus_mgr.get_total_days()
        if target_day > total_days:
            logger.info(f"Target day {target_day} exceeds course length ({total_days} days). Course Complete!")
            return True

        lesson_meta = self.syllabus_mgr.get_lesson(target_day)
        logger.info(f"================ STARTING PUBLISH PIPELINE: Day {target_day} - '{lesson_meta.title}' ================")

        markdown_content = ""
        model_used = "cache"

        # Step 1: Check Cache
        if self.cache_mgr.has_valid_cache(target_day):
            logger.info(f"Cache HIT for Day {target_day}. Fetching pre-generated lesson from cache...")
            cached_data = self.cache_mgr.get_from_cache(target_day)
            if cached_data:
                markdown_content = cached_data["markdown_content"]
                model_used = cached_data.get("model_used", "cached_batch")

        # Step 2: Generate via Gemini if not cached
        if not markdown_content:
            logger.info(f"Cache MISS for Day {target_day}. Generating lesson via Gemini API...")
            prev_summary = self.syllabus_mgr.get_previous_lessons_summary(target_day)
            prompt_text = self.prompt_builder.build_prompt(
                lesson=lesson_meta,
                course_name=self.config.syllabus.course_name,
                previous_lessons_summary=prev_summary
            )

            try:
                gen_result = self.gemini_client.generate_lesson_markdown(prompt_text)
                raw_markdown = gen_result["content"]
                model_used = gen_result["model_used"]

                # Validate Markdown
                markdown_content = MarkdownFormatter.format_lesson(
                    raw_markdown=raw_markdown,
                    lesson_number=target_day,
                    lesson_title=lesson_meta.title
                )
                
                # Cache generated content
                self.cache_mgr.save_to_cache(
                    day=target_day,
                    title=lesson_meta.title,
                    markdown_content=markdown_content,
                    model_used=model_used
                )
            except Exception as exc:
                err_msg = f"Generation/Validation failed for Day {target_day}: {exc}"
                logger.error(err_msg)
                self.recovery_mgr.record_failure(target_day, str(exc), retry_count=3, fallback_used=True)
                flag_recovery_needed(target_day, self.config.state.file_path)
                return False

        if dry_run:
            logger.info(f"[DRY-RUN] Validated lesson Day {target_day} ({len(markdown_content)} bytes). Skipping GitHub push.")
            return True

        # Step 3: Publish Lesson Markdown to Codewithpython
        safe_title = lesson_meta.title.replace(' ', '_').replace('/', '_')
        lesson_filename = f"Day{target_day:03d}_{safe_title}.md"
        commit_msg = f"feat(lesson): publish Day {target_day:03d} - {lesson_meta.title}"

        try:
            self.github_mgr.publish_file(lesson_filename, markdown_content, commit_msg)
            self.cache_mgr.mark_published(target_day)
        except Exception as exc:
            err_msg = f"Failed to push lesson file '{lesson_filename}' to target repo: {exc}"
            logger.error(err_msg)
            self.recovery_mgr.record_failure(target_day, str(exc), retry_count=3)
            flag_recovery_needed(target_day, self.config.state.file_path)
            return False

        # Step 4: Update Progress State
        updated_state = update_progress_after_publish(
            lesson_number=target_day,
            lesson_title=lesson_meta.title,
            file_path=self.config.state.file_path
        )

        # Step 5: Update Target Repository README.md
        try:
            readme_content = ReadmeGenerator.generate_readme(updated_state, self.syllabus_mgr)
            readme_commit_msg = f"docs(readme): update dashboard after Day {target_day:03d} publication"
            self.github_mgr.publish_file("README.md", readme_content, readme_commit_msg)
        except Exception as exc:
            logger.warning(f"Failed to update README.md on target repo: {exc}")

        logger.info(f"================ SUCCESS: Day {target_day} published successfully! ================")
        return True

    def generate_weekly_cache(self) -> int:
        """
        Pre-generates next 7 days of lessons into cache (Run on Sundays).
        """
        state: ProgressState = load_progress(self.config.state.file_path)
        start_day = state.next_lesson
        end_day = min(start_day + 7, self.syllabus_mgr.get_total_days() + 1)

        logger.info(f"Generating weekly cache batch for Days {start_day} to {end_day - 1}...")
        generated_count = 0

        for day in range(start_day, end_day):
            if self.cache_mgr.has_valid_cache(day):
                logger.info(f"Day {day} already cached. Skipping.")
                continue

            lesson_meta = self.syllabus_mgr.get_lesson(day)
            prev_summary = self.syllabus_mgr.get_previous_lessons_summary(day)
            prompt_text = self.prompt_builder.build_prompt(
                lesson=lesson_meta,
                course_name=self.config.syllabus.course_name,
                previous_lessons_summary=prev_summary
            )

            try:
                gen_result = self.gemini_client.generate_lesson_markdown(prompt_text)
                formatted_md = MarkdownFormatter.format_lesson(
                    raw_markdown=gen_result["content"],
                    lesson_number=day,
                    lesson_title=lesson_meta.title
                )
                self.cache_mgr.save_to_cache(
                    day=day,
                    title=lesson_meta.title,
                    markdown_content=formatted_md,
                    model_used=gen_result["model_used"]
                )
                generated_count += 1
                logger.info(f"Cached Day {day} successfully.")
            except Exception as exc:
                logger.error(f"Failed to pre-cache Day {day}: {exc}")
                break

        return generated_count


def main():
    parser = argparse.ArgumentParser(description="GitHubDev Automation Publisher CLI")
    parser.add_argument("--batch-cache", action="store_true", help="Run Sunday weekly batch caching")
    parser.add_argument("--force-day", type=int, help="Force publish a specific day number")
    parser.add_argument("--dry-run", action="store_true", help="Generate and validate without committing to GitHub")
    args = parser.parse_args()

    publisher = Publisher()

    if args.batch_cache:
        count = publisher.generate_weekly_cache()
        logger.info(f"Batch caching completed. {count} lessons added to cache.")
        sys.exit(0)
    else:
        success = publisher.run_daily_publish(force_day=args.force_day, dry_run=args.dry_run)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
