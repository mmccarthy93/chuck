from collections import defaultdict
from threading import Lock

# Store conversations temporarily in RAM
_sessions = defaultdict(list)
_lock = Lock()

MAX_MESSAGES = 20


def get_session_messages(conversation_id: str) -> list[dict]:
    """Return recent messages for a conversation."""
    with _lock:
        return [
            message.copy()
            for message in _sessions[conversation_id]
        ]


def add_session_message(
    conversation_id: str,
    role: str,
    content: str
):
    """Add a message to temporary conversation memory."""
    with _lock:
        _sessions[conversation_id].append({
            "role": role,
            "content": content
        })

        # Keep only the most recent messages
        _sessions[conversation_id] = (
            _sessions[conversation_id][-MAX_MESSAGES:]
        )