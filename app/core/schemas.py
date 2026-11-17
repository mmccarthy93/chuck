from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A provider-independent tool request."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResult:
    """A standardized response from any LLM provider."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    # Opaque provider-specific data needed to continue a tool call.
    continuation: Any = None