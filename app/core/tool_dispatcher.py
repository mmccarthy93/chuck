from app.core.schemas import ToolCall
from app.memory.executor import execute_memory_tool
from app.memory.authorization import is_explicit_memory_recall
from app.memory.facts import get_fact_record

class ToolDispatcher:
    """Validate and execute approved CHUCK tool calls."""

    def execute(
        self,
        tool_call: ToolCall,
        user_message: str,
    ) -> dict:
        """Dispatch an authorized tool request."""

        name = tool_call.name
        arguments = tool_call.arguments

        # Only read-only memory access is enabled for now.
        if name == "recall_memories":

            if not is_explicit_memory_recall(user_message):
                return {
                    "success": False,
                    "error": "Memory inspection not authorized.",
                }

            if arguments:
                return {
                    "success": False,
                    "error": "Unexpected memory arguments.",
                }

            return execute_memory_tool(name, arguments)

        # Memory writes are proposals, never direct executions.
        if name in {"remember_fact", "forget_fact"}:

            if name == "remember_fact":
                required = {"category", "key", "value"}
            else:
                required = {"key"}

            if set(arguments) != required:
                return {
                    "success": False,
                    "error": "Invalid memory tool arguments.",
                }

            if name == "forget_fact":
                record = get_fact_record(arguments["key"])

                if record is None:
                    return {
                        "success": False,
                        "error": "Memory not found.",
                    }

            # Validate and prepare the proposed operation.
            result = execute_memory_tool(name, arguments)

            if result.get("requires_confirmation"):
                return {
                    "success": True,
                    "status": "proposed",
                    "action": name,
                    "arguments": arguments,
                }

            return result

        # Other tools will be enabled in later steps.
        return {
            "success": False,
            "error": f"Tool not authorized: {name}",
        }