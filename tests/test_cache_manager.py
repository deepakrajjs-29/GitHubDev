"""Unit tests for cache_manager module."""

import pytest
from pathlib import Path
from src.cache_manager import CacheManager, CacheError


def test_save_and_retrieve_cache(tmp_path):
    cache_mgr = CacheManager(cache_dir=str(tmp_path))
    markdown = "# Day 001: Hello World"
    
    file_path = cache_mgr.save_to_cache(
        day=1,
        title="Intro",
        markdown_content=markdown,
        model_used="gemini-2.5-flash"
    )
    assert file_path.exists()
    assert cache_mgr.has_valid_cache(1) is True
    
    data = cache_mgr.get_from_cache(1)
    assert data["day"] == 1
    assert data["markdown_content"] == markdown
    assert data["model_used"] == "gemini-2.5-flash"
    assert data["published"] is False


def test_cache_corrupted_hash(tmp_path):
    cache_mgr = CacheManager(cache_dir=str(tmp_path))
    file_path = cache_mgr.save_to_cache(
        day=2,
        title="Variables",
        markdown_content="Original Content",
        model_used="gemini-2.5-flash"
    )
    
    # Tamper with file
    file_path.write_text('{"day": 2, "markdown_content": "Tampered Content", "content_hash": "wrong_hash"}')
    
    assert cache_mgr.has_valid_cache(2) is False
    assert cache_mgr.get_from_cache(2) is None
