"""Recovery and failure audit logging manager for GitHubDev engine."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("GitHubDev.RecoveryManager")


class RecoveryManager:
    """Manages failure recording in backup/automation_log.md and handles recovery flags."""

    def __init__(self, log_path: str = "backup/automation_log.md", base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.cwd()
            
        full_path = Path(log_path)
        if not full_path.is_absolute():
            full_path = base_dir / log_path
            
        self.log_path = full_path
        self._ensure_file_header()

    def _ensure_file_header(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            header = (
                "# Automation Audit & Recovery Log\n\n"
                "This document records any failure, recovery action, or manual intervention performed by the GitHubDev automation engine.\n\n"
                "| Timestamp | Lesson Number | Failure Reason | Retry Count | Fallback Used | Execution Status |\n"
                "| :--- | :---: | :--- | :---: | :---: | :---: |\n"
            )
            self.log_path.write_text(header, encoding="utf-8")

    def record_failure(
        self,
        lesson_number: int,
        reason: str,
        retry_count: int = 3,
        fallback_used: bool = False
    ) -> None:
        """Appends failure row to backup/automation_log.md."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        fallback_str = "Yes" if fallback_used else "No"
        # Sanitize pipe chars in reason
        clean_reason = reason.replace("|", "-").replace("\n", " ")
        
        row = f"| {now_str} | Day {lesson_number:03d} | {clean_reason} | {retry_count} | {fallback_str} | FAILED |\n"
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(row)
            logger.info(f"Recorded failure for Day {lesson_number} to {self.log_path}")
        except Exception as exc:
            logger.error(f"Failed to write recovery log to {self.log_path}: {exc}")
