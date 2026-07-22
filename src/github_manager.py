"""GitHub REST API and repository manager for cross-repository publishing."""

import base64
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import requests

from src.config_loader import RepositoryConfig, GitHubConfig

logger = logging.getLogger("GitHubDev.GitHubManager")


class GitHubManagerError(Exception):
    """Raised when GitHub API operations fail after retries."""
    pass


class GitHubManager:
    """Manages cross-repository commits and updates to target repo via GitHub REST API."""

    def __init__(self, repo_config: RepositoryConfig, github_config: GitHubConfig):
        self.owner = repo_config.owner
        self.target_repo = repo_config.target_repo.split("/")[-1]
        self.branch = repo_config.target_branch
        self.token = github_config.pat_token or os.getenv("GH_PAT") or os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubDev-Automation-Engine"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def get_file_sha(self, target_path: str) -> Optional[str]:
        """Fetches current SHA of target file if it already exists on target repo branch."""
        url = f"{self.base_url}/repos/{self.owner}/{self.target_repo}/contents/{target_path}"
        params = {"ref": self.branch}
        
        try:
            res = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
            if res.status_code == 200:
                return res.json().get("sha")
            elif res.status_code == 404:
                return None
            else:
                logger.warning(f"Unexpected status {res.status_code} when fetching file SHA for '{target_path}'")
                return None
        except Exception as exc:
            logger.warning(f"Exception fetching file SHA from GitHub: {exc}")
            return None

    def publish_file(self, target_path: str, content_str: str, commit_message: str) -> bool:
        """
        Creates or updates a file in the target repository via GitHub REST API.
        
        Args:
            target_path: Path in target repo (e.g. Day001_Introduction.md or README.md)
            content_str: UTF-8 markdown string content
            commit_message: Commit message string
            
        Returns:
            True on successful commit/push
        """
        # If running locally and target folder exists locally, also write to local target directory
        local_target_dir = Path.cwd().parent / self.target_repo
        if local_target_dir.exists():
            local_file = local_target_dir / target_path
            local_file.parent.mkdir(parents=True, exist_ok=True)
            local_file.write_text(content_str, encoding="utf-8")
            logger.info(f"Local target update: Wrote '{target_path}' to {local_target_dir}")

        if not self.token:
            logger.warning("No GH_PAT configured. Local file written; skipping GitHub REST API push.")
            return True

        url = f"{self.base_url}/repos/{self.owner}/{self.target_repo}/contents/{target_path}"
        sha = self.get_file_sha(target_path)
        encoded_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": self.branch
        }
        if sha:
            payload["sha"] = sha

        for attempt in range(1, 4):
            try:
                logger.info(f"Pushing '{target_path}' to GitHub target repo '{self.owner}/{self.target_repo}' (Attempt {attempt}/3)...")
                res = requests.put(url, headers=self._get_headers(), json=payload, timeout=15)

                if res.status_code in (200, 201):
                    commit_sha = res.json().get("commit", {}).get("sha", "unknown")
                    logger.info(f"Successfully committed '{target_path}' (Commit SHA: {commit_sha})")
                    return True
                else:
                    logger.warning(f"GitHub API Error HTTP {res.status_code}: {res.text}")
            except Exception as exc:
                logger.warning(f"Network error on attempt {attempt}: {exc}")

        raise GitHubManagerError(f"Failed to publish '{target_path}' to target repository after 3 attempts.")
