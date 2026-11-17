import re

from app.memory.facts import (
    save_fact,
    get_fact,
    delete_fact,
)


def handle_memory_command(message: str) -> str | None:
    """Handle explicit memory commands."""

    text = message.strip()

    # Remember a fact
    match = re.fullmatch(
        r"remember that my (.+?) is (.+?)[.!]?",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        subject, value = match.groups()

        key = subject.strip().lower().replace(" ", "_")
        value = value.strip()

        save_fact("personal", key, value)

        return f"Remembered: your {subject} is {value}."

    # Recall a fact
    match = re.fullmatch(
        r"what(?:'s| is) my (.+?)[?.!]?",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        subject = match.group(1)
        key = subject.strip().lower().replace(" ", "_")

        value = get_fact(key)

        if value is not None:
            return f"Your {subject} is {value}."

        return f"I don't have your {subject} saved."

    # Forget a fact
    match = re.fullmatch(
        r"forget my (.+?)[.!]?",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        subject = match.group(1)
        key = subject.strip().lower().replace(" ", "_")

        deleted = delete_fact(key)

        if deleted:
            return f"Forgotten: your {subject}."

        return f"I don't have your {subject} saved."

    return None