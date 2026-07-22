"""Gemini API client with exponential backoff and automatic model fallback for GitHubDev engine."""

import time
import os
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.config_loader import GeminiConfig

logger = logging.getLogger("GitHubDev.GeminiClient")


class GeminiError(Exception):
    """Raised when Gemini API request fails across both primary and fallback models."""
    pass


class GeminiClient:
    """Client for generating content via Gemini API with retry logic and model fallbacks."""

    def __init__(self, config: GeminiConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise GeminiError("Gemini API key not configured. Set GEMINI_API_KEY in environment or GitHub Secrets.")

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as exc:
            raise GeminiError(f"Failed to initialize Google GenAI client: {exc}") from exc

    def generate_lesson_markdown(self, prompt_text: str) -> Dict[str, Any]:
        """
        Generates markdown lesson text from Gemini using primary model with fallback to secondary model.

        Strategy:
        1. Attempt primary model (gemini-2.5-flash) up to retry_count times.
        2. If primary fails, attempt fallback model (gemini-1.5-pro) up to retry_count times.
        3. Returns dict containing 'content', 'model_used', and 'duration_seconds'.
        """
        start_time = time.time()

        # Step 1: Try Primary Model
        primary_model = self.config.primary_model
        logger.info(f"Attempting generation with Primary Model: '{primary_model}'...")
        content = self._attempt_model_with_retries(primary_model, prompt_text)

        if content:
            duration = round(time.time() - start_time, 2)
            logger.info(f"Successfully generated content using '{primary_model}' in {duration}s")
            return {
                "content": content,
                "model_used": primary_model,
                "duration_seconds": duration
            }

        # Step 2: Fallback to Secondary Model
        fallback_model = self.config.fallback_model
        logger.warning(f"Primary model '{primary_model}' failed all retry attempts. Switching to Fallback Model: '{fallback_model}'...")
        content = self._attempt_model_with_retries(fallback_model, prompt_text)

        if content:
            duration = round(time.time() - start_time, 2)
            logger.info(f"Successfully generated content using Fallback Model '{fallback_model}' in {duration}s")
            return {
                "content": content,
                "model_used": fallback_model,
                "duration_seconds": duration
            }

        # Step 3: All Models Failed
        duration = round(time.time() - start_time, 2)
        raise GeminiError(
            f"Gemini generation failed on both primary ('{primary_model}') and fallback ('{fallback_model}') models after full retries."
        )

    def _attempt_model_with_retries(self, model_name: str, prompt_text: str) -> Optional[str]:
        """Helper to call Gemini model with exponential backoff retries."""
        delay = self.config.retry_delay_seconds
        gen_config = types.GenerateContentConfig(
            temperature=self.config.temperature,
        )

        for attempt in range(1, self.config.retry_count + 1):
            try:
                logger.info(f"Calling model '{model_name}' (Attempt {attempt}/{self.config.retry_count})...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=gen_config
                )

                if response and response.text and response.text.strip():
                    return response.text.strip()
                else:
                    logger.warning(f"Model '{model_name}' returned empty or null output on attempt {attempt}.")

            except Exception as exc:
                logger.warning(f"API Exception on '{model_name}' attempt {attempt}/{self.config.retry_count}: {exc}")

            if attempt < self.config.retry_count:
                logger.info(f"Waiting {delay}s before next retry...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff

        return None
