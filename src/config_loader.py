"""Configuration loader and validation module for GitHubDev automation engine."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


class ProjectConfig(BaseModel):
    name: str = Field(default="GitHubDev Automation System")
    version: str = Field(default="1.0.0")
    author: str = Field(default="Deepak Raj JS")


class RepositoryConfig(BaseModel):
    engine_repo: str = Field(default="deepakrajjs-29/GitHubDev")
    target_repo: str = Field(default="deepakrajjs-29/Codewithpython")
    owner: str = Field(default="deepakrajjs-29")
    target_branch: str = Field(default="main")
    engine_branch: str = Field(default="main")


class SchedulingConfig(BaseModel):
    timezone: str = Field(default="UTC")
    daily_publish_time: str = Field(default="00:00")
    weekly_cache_day: str = Field(default="Sunday")


class GeminiConfig(BaseModel):
    primary_model: str = Field(default="gemini-2.0-flash")
    fallback_model: str = Field(default="gemini-1.5-flash")
    retry_count: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: int = Field(default=5, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    secret_name: str = Field(default="GEMINI_API_KEY")
    api_key: Optional[str] = None


class CacheConfig(BaseModel):
    enabled: bool = Field(default=True)
    generate_weekly: bool = Field(default=True)
    cache_days: int = Field(default=7, ge=1)
    cache_directory: str = Field(default="cache")


class PublishingConfig(BaseModel):
    lesson_prefix: str = Field(default="Day")
    number_padding: int = Field(default=3, ge=1)
    file_extension: str = Field(default=".md")
    target_directory: str = Field(default=".")


class StateConfig(BaseModel):
    file_path: str = Field(default="state/progress.json")


class SyllabusConfig(BaseModel):
    file_path: str = Field(default="syllabus/python_90_days.json")
    course_name: str = Field(default="Python 90 Days Mastery")
    total_days: int = Field(default=90, ge=1)


class PromptConfig(BaseModel):
    template_path: str = Field(default="prompts/python_lesson_prompt.md")


class LoggingConfig(BaseModel):
    log_directory: str = Field(default="logs")
    backup_directory: str = Field(default="backup")
    automation_log_file: str = Field(default="backup/automation_log.md")
    level: str = Field(default="INFO")


class GitHubConfig(BaseModel):
    pat_secret_name: str = Field(default="GH_PAT")
    pat_token: Optional[str] = None


class AppConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    repositories: RepositoryConfig = Field(default_factory=RepositoryConfig)
    scheduling: SchedulingConfig = Field(default_factory=SchedulingConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    publishing: PublishingConfig = Field(default_factory=PublishingConfig)
    state: StateConfig = Field(default_factory=StateConfig)
    syllabus: SyllabusConfig = Field(default_factory=SyllabusConfig)
    prompt: PromptConfig = Field(default_factory=PromptConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)


class ConfigError(Exception):
    """Raised when configuration validation or file reading fails."""
    pass


def load_config(config_path: str = "config/config.yaml", base_dir: Optional[Path] = None) -> AppConfig:
    """
    Loads and validates application configuration from YAML and environment variables.
    
    Args:
        config_path: Relative or absolute path to config.yaml
        base_dir: Optional base directory for relative path resolution
        
    Returns:
        Validated AppConfig object
        
    Raises:
        ConfigError: If config file is missing or contains invalid fields
    """
    if base_dir is None:
        base_dir = Path.cwd()
        
    full_path = Path(config_path)
    if not full_path.is_absolute():
        full_path = base_dir / config_path
        
    if not full_path.exists():
        raise ConfigError(f"Configuration file not found at: {full_path}")
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML configuration: {exc}") from exc

    try:
        config = AppConfig(**raw_data)
    except ValidationError as exc:
        raise ConfigError(f"Configuration validation error:\n{exc}") from exc

    # Inject environment secrets
    config.gemini.api_key = os.getenv(config.gemini.secret_name) or os.getenv("GEMINI_API_KEY")
    config.github.pat_token = os.getenv(config.github.pat_secret_name) or os.getenv("GH_PAT") or os.getenv("GITHUB_PAT")

    return config
