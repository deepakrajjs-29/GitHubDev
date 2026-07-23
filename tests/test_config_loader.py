"""Unit tests for config_loader module."""

import os
import pytest
from pathlib import Path
from src.config_loader import load_config, AppConfig, ConfigError


def test_load_valid_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
project:
  name: "Test Project"
gemini:
  primary_model: "gemini-flash-latest"
  retry_count: 3
""")
    
    config = load_config(str(config_file))
    assert isinstance(config, AppConfig)
    assert config.project.name == "Test Project"
    assert config.gemini.primary_model == "gemini-flash-latest"
    assert config.gemini.retry_count == 3


def test_load_nonexistent_config():
    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config("non_existent_config_file_path.yaml")


def test_config_validation_error(tmp_path):
    config_file = tmp_path / "invalid_config.yaml"
    config_file.write_text("""
gemini:
  retry_count: -5
""")
    with pytest.raises(ConfigError, match="Configuration validation error"):
        load_config(str(config_file))


def test_env_secrets_injection(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("project: {name: 'Test'}")
    
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key_123")
    monkeypatch.setenv("GH_PAT", "test_github_pat_456")
    monkeypatch.setenv("GITHUB_PAT", "test_github_pat_456")
    
    config = load_config(str(config_file))
    assert config.gemini.api_key == "test_gemini_key_123"
    assert config.github.pat_token == "test_github_pat_456"
