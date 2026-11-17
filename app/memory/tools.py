MEMORY_TOOLS = [
    {
        "type": "function",
        "name": "remember_fact",
        "description": (
            "Save or update a persistent user fact. "
            "Use when the user explicitly asks you to remember "
            "something or clearly states a change to a previously "
            "saved preference. Do not silently save sensitive facts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category such as preferences, personal, or projects."
                },
                "key": {
                    "type": "string",
                    "description": "Stable snake_case identifier, e.g. favorite_cocktail."
                },
                "value": {
                    "type": "string",
                    "description": "The information to remember."
                }
            },
            "required": ["category", "key", "value"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "recall_memories",
        "description": (
            "Retrieve saved facts about the user. "
            "Use when asked what you remember, or when "
            "looking up existing preferences."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "forget_fact",
        "description": (
            "Request deletion of a saved fact. "
            "The application must authorize deletion before execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The memory key to delete."
                }
            },
            "required": ["key"],
            "additionalProperties": False
        },
        "strict": True
    }
]