"""Unit tests for gemini_client module."""

import pytest
from unittest.mock import MagicMock, patch
from src.config_loader import GeminiConfig
from src.gemini_client import GeminiClient, GeminiError


def test_gemini_client_init_missing_key():
    config = GeminiConfig(secret_name="NON_EXISTENT_KEY")
    config.api_key = None
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(GeminiError, match="Gemini API key not configured"):
            GeminiClient(config)


def test_gemini_primary_success():
    config = GeminiConfig(api_key="mock_key", primary_model="gemini-2.5-flash", retry_count=1)
    
    with patch("src.gemini_client.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "# Day 001: Test Lesson Content"
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        client = GeminiClient(config)
        result = client.generate_lesson_markdown("Test Prompt")
        
        assert result["model_used"] == "gemini-2.5-flash"
        assert result["content"] == "# Day 001: Test Lesson Content"


def test_gemini_fallback_trigger():
    config = GeminiConfig(
        api_key="mock_key",
        primary_model="gemini-2.5-flash",
        fallback_model="gemini-1.5-pro",
        retry_count=1,
        retry_delay_seconds=1
    )
    
    with patch("src.gemini_client.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        
        def side_effect(*args, **kwargs):
            model = kwargs.get("model") or (args[0] if args else None)
            if model == "gemini-2.5-flash":
                raise Exception("Primary model quota exceeded")
            mock_resp = MagicMock()
            mock_resp.text = "# Fallback Lesson Content"
            return mock_resp
            
        mock_client.models.generate_content.side_effect = side_effect
        mock_client_cls.return_value = mock_client
        
        client = GeminiClient(config)
        result = client.generate_lesson_markdown("Test Prompt")
        
        assert result["model_used"] == "gemini-1.5-pro"
        assert result["content"] == "# Fallback Lesson Content"
