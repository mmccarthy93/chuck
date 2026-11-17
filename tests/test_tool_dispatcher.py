from unittest.mock import patch

from app.core.schemas import ToolCall
from app.core.tool_dispatcher import ToolDispatcher


def make_tool(name, arguments=None):
    return ToolCall(
        id="test_call",
        name=name,
        arguments=arguments or {},
    )


def test_unauthorized_tool_is_rejected():
    dispatcher = ToolDispatcher()

    result = dispatcher.execute(
        make_tool("delete_everything"),
        "Hello Chuck.",
    )

    assert result["success"] is False


def test_memory_write_is_only_proposed():
    dispatcher = ToolDispatcher()

    call = make_tool(
        "remember_fact",
        {
            "category": "test",
            "key": "favorite_color",
            "value": "Blue",
        },
    )

    with patch(
        "app.core.tool_dispatcher.execute_memory_tool",
        return_value={"requires_confirmation": True},
    ) as mock_executor:

        result = dispatcher.execute(
            call,
            "Remember that my favorite color is blue.",
        )

    assert result["status"] == "proposed"
    assert result["action"] == "remember_fact"
    assert result["arguments"]["value"] == "Blue"

    mock_executor.assert_called_once()


def test_invalid_memory_arguments_are_rejected():
    dispatcher = ToolDispatcher()

    call = make_tool(
        "remember_fact",
        {
            "key": "favorite_color",
            # Missing category and value
        },
    )

    result = dispatcher.execute(
        call,
        "Remember my favorite color.",
    )

    assert result["success"] is False


def test_memory_recall_requires_authorization():
    dispatcher = ToolDispatcher()

    call = make_tool("recall_memories")

    with patch(
        "app.core.tool_dispatcher.execute_memory_tool"
    ) as mock_executor:

        result = dispatcher.execute(
            call,
            "Hello Chuck.",
        )

    assert result["success"] is False
    mock_executor.assert_not_called()