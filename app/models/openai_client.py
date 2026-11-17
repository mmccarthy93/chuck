import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.core.context import build_context
from app.core.schemas import LLMResult
from app.models.base import BaseLLM
from app.models.openai_adapter import parse_openai_response
from app.memory.tools import MEMORY_TOOLS
from app.memory.authorization import is_explicit_memory_recall, is_memory_question
from app.memory.executor import execute_memory_tool

load_dotenv()


class OpenAIClient(BaseLLM):
    def __init__(self):
        self.client = OpenAI()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

   
    def request(
        self,
        messages: list[dict],
        instructions: str,
        tools: list[dict] | None = None,
    ) -> LLMResult:
        """Send a request to OpenAI without executing tools."""

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=messages,
            tools=tools or [],
            parallel_tool_calls=False,
            reasoning={"effort": "minimal"},
            max_output_tokens=1000,
            store=False,
        )

        return parse_openai_response(response)

    def continue_with_tools(
        self,
        messages: list[dict],
        instructions: str,
        continuation,
        tool_results: list[dict],
    ) -> LLMResult:
        """Continue an OpenAI response using executed tool results."""

        input_items = list(messages)

        # Preserve the original model response and tool calls.
        input_items.extend(continuation)

        # Supply each tool's execution result.
        for result in tool_results:
            input_items.append({
                "type": "function_call_output",
                "call_id": result["call_id"],
                "output": json.dumps(result["output"]),
            })

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=input_items,
            reasoning={"effort": "minimal"},
            max_output_tokens=1000,
            store=False,
        )

        return parse_openai_response(response)