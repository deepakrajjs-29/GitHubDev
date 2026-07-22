"""Unit tests for github_manager module."""

import pytest
from unittest.mock import patch, MagicMock
from src.config_loader import RepositoryConfig, GitHubConfig
from src.github_manager import GitHubManager, GitHubManagerError


def test_github_manager_local_and_api():
    repo_cfg = RepositoryConfig(owner="deepakrajjs-29", target_repo="Codewithpython", target_branch="main")
    gh_cfg = GitHubConfig(pat_token="mock_pat_token")
    
    with patch("src.github_manager.requests.put") as mock_put, \
         patch("src.github_manager.requests.get") as mock_get:
        
        mock_get_res = MagicMock()
        mock_get_res.status_code = 404
        mock_get.return_value = mock_get_res
        
        mock_put_res = MagicMock()
        mock_put_res.status_code = 201
        mock_put_res.json.return_value = {"commit": {"sha": "abc12345"}}
        mock_put.return_value = mock_put_res
        
        gh_mgr = GitHubManager(repo_cfg, gh_cfg)
        success = gh_mgr.publish_file("Day001_Introduction.md", "# Content", "Add Day 001")
        
        assert success is True
        mock_put.assert_called_once()
