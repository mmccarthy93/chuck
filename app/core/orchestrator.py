from app.memory.session import (
    get_session_messages,
    add_session_message,
)
from app.models.base import BaseLLM
from app.memory.pending import (
    get_pending_action,
    clear_pending_action,
    create_pending_action
)
from app.memory.executor import commit_memory_action
from app.memory.authorization import (
    is_explicit_memory_command,
    is_memory_question,
    is_explicit_memory_recall
)
from app.core.context import build_context
from app.core.tool_dispatcher import ToolDispatcher
from app.core.schemas import ToolCall
from app.memory.tools import MEMORY_TOOLS

class ChuckOrchestrator:
    """Coordinates CHUCK's conversations and LLM."""

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.dispatcher = ToolDispatcher()


    def handle_confirmation(
        self,
        conversation_id: str,
        message: str,
    ) -> dict | None:
        """Process a pending memory confirmation."""

        pending = get_pending_action(conversation_id)

        if pending is None:
            return None

        answer = message.lower().strip(" .!?")

        approved = {
            "yes", "y", "confirm", "sure",
            "go ahead", "do it"
        }

        rejected = {
            "no", "n", "cancel", "never mind", "nope"
        }

        if answer in approved:
            # Consume the pending action before executing.
            clear_pending_action(conversation_id)

            result = commit_memory_action(
                pending["action"],
                pending["arguments"]
            )

            if result["success"]:
                reply = (
                    f"Done. Memory {result['action']}: "
                    f"{result['key']}."
                )
            else:
                reply = result.get(
                    "message",
                    "I couldn't complete that memory operation."
                )

        elif answer in rejected:
            clear_pending_action(conversation_id)
            reply = "Understood. No memory changes made."

        else:
            # A new request replaces the pending confirmation.
            clear_pending_action(conversation_id)
            return None

        add_session_message(conversation_id, "user", message)
        add_session_message(conversation_id, "assistant", reply)

        return {
            "conversation_id": conversation_id,
            "response": reply,
        }

    def chat(self, conversation_id: str, message: str) -> dict:
        """Handle a complete CHUCK conversation turn."""

        message = message.strip()

        if not message:
            return {
                "conversation_id": conversation_id,
                "response": "You've said precisely nothing. Impressive.",
            }

        # STEP 1: Handle pending memory confirmations.
        confirmation = self.handle_confirmation(
            conversation_id,
            message,
        )

        if confirmation is not None:
            return confirmation

        # STEP 2: Generate a response using the new tool system.
        reply = self.run_tool_cycle(
            conversation_id=conversation_id,
            message=message,
        )

        # STEP 3: Store temporary conversation context.
        add_session_message(conversation_id, "user", message)
        add_session_message(conversation_id, "assistant", reply)

        return {
            "conversation_id": conversation_id,
            "response": reply,
        }

    def run_tool_cycle(
        self,
        conversation_id: str,
        message: str,
    ) -> str:
        """Execute one read-only LLM tool cycle."""

        # 1. Build conversation context
        history = get_session_messages(conversation_id)

        messages = history + [
            {"role": "user", "content": message}
        ]

        instructions = build_context(messages)

        # 2. Determine permitted tools.
        if is_explicit_memory_recall(message):
            allowed_names = {"recall_memories"}
        elif is_memory_question(message):
            allowed_names = set()
        else:
            # Writes are only proposals at this stage.
            allowed_names = {"remember_fact", "forget_fact"}

        available_tools = [
            tool for tool in MEMORY_TOOLS
            if tool["name"] in allowed_names
        ]

        # 3. Ask the LLM
        result = self.llm.request(
            messages=messages,
            instructions=instructions,
            tools=available_tools,
        )

        # 4. Return immediately if no tools requested
        if not result.tool_calls:
            return result.text

        # 5. Execute tool requests through the dispatcher
        tool_results = []

        for call in result.tool_calls:

            # Memory changes require orchestration and authorization.
            if call.name in {"remember_fact", "forget_fact"}:
                return self.handle_tool_proposal(
                    conversation_id=conversation_id,
                    message=message,
                    tool_call=call,
                )

            # Read-only tools execute through the dispatcher.
            outcome = self.dispatcher.execute(
                tool_call=call,
                user_message=message,
            )

            tool_results.append({
                "call_id": call.id,
                "output": outcome,
            })


        # 6. Return the results to the same LLM
        final_result = self.llm.continue_with_tools(
            messages=messages,
            instructions=instructions,
            continuation=result.continuation,
            tool_results=tool_results,
        )

        # Prevent further tool execution in this prototype
        if final_result.tool_calls:
            return (
                "I couldn't finish that request "
                "within the permitted tool operations."
            )

        return final_result.text


    def handle_tool_proposal(
        self,
        conversation_id: str,
        message: str,
        tool_call: ToolCall,
    ) -> str:
        """Authorize, execute, or queue a proposed memory action."""

        action = tool_call.name

        if action not in {"remember_fact", "forget_fact"}:
            return "Unsupported memory operation."

        # Reject write requests triggered by ordinary questions.
        if is_memory_question(message):
            return "No memory changes made."

        # Validate the proposed operation through the dispatcher.
        result = self.dispatcher.execute(
            tool_call=tool_call,
            user_message=message,
        )

        if result.get("status") != "proposed":
            return result.get(
                "error",
                "I couldn't prepare that memory change.",
            )

        arguments = result["arguments"]

        # Execute explicitly authorized instructions immediately.
        if is_explicit_memory_command(message, action):
            outcome = commit_memory_action(
                action,
                arguments,
            )

            if outcome["success"]:
                return (
                    f"Done. Memory {outcome['action']}: "
                    f"{outcome['key']}."
                )

            return outcome.get(
                "message",
                "I couldn't complete that memory operation.",
            )

        # Otherwise, request confirmation.
        create_pending_action(
            conversation_id,
            action,
            arguments,
        )

        label = "save" if action == "remember_fact" else "delete"

        return f"Shall I {label} this memory? {arguments}"