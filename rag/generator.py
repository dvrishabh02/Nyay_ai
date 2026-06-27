"""
Groq generator — calls llama-3.3-70b-versatile through Groq's OpenAI-compatible
chat completions endpoint.
"""

from loguru import logger
from openai import OpenAI

from rag.config import (
    GENERATION_MAX_TOKENS,
    GENERATION_TEMPERATURE,
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
)


class GroqGenerator:
    """Thin wrapper over the OpenAI SDK pointed at Groq."""

    def __init__(self):
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to .env (see .env.example)."
            )
        self._client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
        self._model = GROQ_MODEL
        logger.info(f"GroqGenerator ready: model={self._model}")

    def generate(self, messages: list[dict]) -> str:
        """Run a chat completion and return the assistant text."""
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=GENERATION_TEMPERATURE,
            max_tokens=GENERATION_MAX_TOKENS,
        )
        return resp.choices[0].message.content.strip()
