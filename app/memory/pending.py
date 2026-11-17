from datetime import datetime, timedelta, timezone
from threading import Lock

# Pending actions live in RAM, never in permanent memory.
_pending_actions = {}
_lock = Lock()

EXPIRATION_MINUTES = 5


def create_pending_action(
    conversation_id: str,
    action: str,
    arguments: dict
):
    """Store an action awaiting user confirmation."""

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=EXPIRATION_MINUTES
    )

    with _lock:
        _pending_actions[conversation_id] = {
            "action": action,
            "arguments": arguments.copy(),
            "expires_at": expires_at,
        }


def get_pending_action(conversation_id: str):
    """Retrieve a pending action if it hasn't expired."""

    with _lock:
        pending = _pending_actions.get(conversation_id)

        if pending is None:
            return None

        if datetime.now(timezone.utc) >= pending["expires_at"]:
            del _pending_actions[conversation_id]
            return None

        return {
            "action": pending["action"],
            "arguments": pending["arguments"].copy(),
        }


def clear_pending_action(conversation_id: str):
    """Remove a pending action after approval or rejection."""

    with _lock:
        return _pending_actions.pop(conversation_id, None)