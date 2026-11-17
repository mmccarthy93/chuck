import re


def is_explicit_memory_command(message: str, action: str) -> bool:
    """
    Determine whether the user explicitly requested
    a particular memory operation.
    """

    text = message.strip().lower()

    # Remove optional CHUCK wake phrase
    text = re.sub(r"^(hey\s+)?chuck[,\s:!]+", "", text)

    patterns = {
        "remember_fact": [
            r"^(please\s+)?remember\b",
            r"^(please\s+)?save\b",
            r"^(please\s+)?store\b",
            r"^(please\s+)?make a note\b",
            r"^(please\s+)?update\b",
            r"^(please\s+)?change my\b",
            r"^(please\s+)?set my\b",
        ],
        "forget_fact": [
            r"^(please\s+)?forget\b",
            r"^(please\s+)?delete\b",
            r"^(please\s+)?remove\b",
            r"^(please\s+)?erase\b",
        ],
    }

    return any(
        re.search(pattern, text)
        for pattern in patterns.get(action, [])
    )

def is_explicit_memory_recall(message: str) -> bool:
    """Check whether the user explicitly requested memory inspection."""

    text = message.strip().lower()

    # Remove optional CHUCK prefix.
    text = re.sub(r"^(hey\s+)?chuck[,\s:!]+", "", text)

    patterns = [
        r"\bwhat do you remember\b",
        r"\bwhat (?:do you|have you) (?:know|saved|stored) about me\b",
        r"\b(?:show|list|display|review|inspect)\b.{0,50}\bmemor(?:y|ies)\b",
        r"\b(?:show|list|display)\b.{0,50}\b(?:saved|stored) facts\b",
        r"\beverything you (?:remember|know) about me\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)

def is_memory_question(message: str) -> bool:
    """Detect straightforward questions about existing memories."""

    text = message.strip().lower()

    text = re.sub(r"^(hey\s+)?chuck[,\s:!]+", "", text)

    patterns = [
        r"^(?:what(?:'?s| is| was)|who|where|when|which)\b",
        r"^(?:do you remember|do you know|can you recall)\b",
        r"^(?:tell me|remind me)\b.*\b(?:my|about me)\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)