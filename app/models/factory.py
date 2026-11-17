import os

from app.models.base import BaseLLM
from app.models.openai_client import OpenAIClient


def create_llm() -> BaseLLM:
    """Create an LLM based on the configured provider."""

    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        return OpenAIClient()

    raise ValueError(f"Unsupported LLM provider: {provider}")