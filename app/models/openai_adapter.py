import json

from app.core.schemas import LLMResult, ToolCall


def parse_openai_response(response) -> LLMResult:
    """Convert an OpenAI response into CHUCK's standard format."""

    tool_calls = []

    for item in response.output:
        if item.type == "function_call":
            tool_calls.append(
                ToolCall(
                    id=item.call_id,
                    name=item.name,
                    arguments=json.loads(item.arguments),
                )
            )

    return LLMResult(
        text=response.output_text or "",
        tool_calls=tool_calls,
        continuation=[
            item.model_dump(exclude_none=True)
            for item in response.output
        ],
    )