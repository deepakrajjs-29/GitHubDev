"""Weekly batch cache manager module for GitHubDev engine."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


class CacheError(Exception):
    """Raised when reading, writing, or validating cache files fails."""
    pass


class CacheManager:
    """Manages pre-generated lesson batch caching inside cache/ directory."""

    def __init__(self, cache_dir: str = "cache", base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.cwd()
            
        full_path = Path(cache_dir)
        if not full_path.is_absolute():
            full_path = base_dir / cache_dir
            
        self.cache_dir = full_path
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file_path(self, day: int) -> Path:
        return self.cache_dir / f"Day{day:03d}.json"

    @staticmethod
    def compute_content_hash(text: str) -> str:
        """Computes SHA256 hash of markdown content string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def save_to_cache(
        self,
        day: int,
        title: str,
        markdown_content: str,
        model_used: str
    ) -> Path:
        """
        Saves lesson markdown and metadata to JSON cache file.
        """
        cache_path = self._get_cache_file_path(day)
        content_hash = self.compute_content_hash(markdown_content)
        now_iso = datetime.now(timezone.utc).isoformat()

        payload = {
            "day": day,
            "title": title,
            "markdown_content": markdown_content,
            "generated_at": now_iso,
            "model_used": model_used,
            "content_hash": content_hash,
            "published": False
        }

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return cache_path
        except Exception as exc:
            raise CacheError(f"Failed to write cache for Day {day}: {exc}") from exc

    def get_from_cache(self, day: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached lesson data for specified day, verifying hash integrity.
        """
        cache_path = self._get_cache_file_path(day)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            content = data.get("markdown_content", "")
            stored_hash = data.get("content_hash", "")
            computed_hash = self.compute_content_hash(content)

            if stored_hash != computed_hash:
                raise CacheError(f"Corrupted cache file for Day {day}: Hash mismatch.")

            return data
        except (json.JSONDecodeError, CacheError) as exc:
            # Delete corrupted cache entry safely
            if cache_path.exists():
                cache_path.unlink()
            return None

    def has_valid_cache(self, day: int) -> bool:
        """Checks if a valid, uncorrupted cache exists for specified day."""
        return self.get_from_cache(day) is not None

    def mark_published(self, day: int) -> None:
        """Updates cache entry status to published = True."""
        data = self.get_from_cache(day)
        if data:
            data["published"] = True
            cache_path = self._get_cache_file_path(day)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
