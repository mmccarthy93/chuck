from abc import ABC, abstractmethod
from app.core.schemas import LLMResult
from typing import Any


class BaseLLM(ABC):
    """Common interface for CHUCK's language models."""


    @abstractmethod
    def request(
        self,
        messages: list[dict],
        instructions: str,
        tools: list[dict] | None = None,
    ) -> LLMResult:
        """Generate a standardized response without executing tools."""
        pass

    @abstractmethod
    def continue_with_tools(
        self,
        messages: list[dict],
        instructions: str,
        continuation: Any,
        tool_results: list[dict],
    ) -> LLMResult:
        """Continue an LLM response after tool execution."""
        pass