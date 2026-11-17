import re

from app.memory.facts import (
    save_fact,
    get_fact,
    get_all_facts,
    delete_fact,
    get_cloud_facts,
    get_fact_record,
    CLOUD_ALLOWED_LEVELS
)


def validate_memory(category: str, key: str, value: str):
    """Validate a proposed memory before allowing storage."""

    if not all(isinstance(x, str) for x in (category, key, value)):
        raise ValueError("Memory fields must be strings.")

    if not re.fullmatch(r"[a-z][a-z0-9_]{0,99}", key):
        raise ValueError("Invalid memory key.")

    if not category.strip() or len(category) > 50:
        raise ValueError("Invalid memory category.")

    if not value.strip() or len(value) > 2000:
        raise ValueError("Invalid memory value.")


def execute_memory_tool(name: str, arguments: dict) -> dict:
    """Validate memory operations before execution."""

    if name == "recall_memories":
        return {
            "success": True,
            "memories": get_cloud_facts(),
        }

    if name == "remember_fact":
        category = arguments["category"]
        key = arguments["key"]
        value = arguments["value"]

        validate_memory(category, key, value)

        # Request authorization before changing persistent memory.
        return {
            "success": False,
            "requires_confirmation": True,
            "action": "remember_fact",
            "category": category,
            "key": key,
            "value": value,
            "message": f"Confirm saving {key}: {value}",
        }

    if name == "forget_fact":
        key = arguments["key"]

        if not isinstance(key, str):
            raise ValueError("Invalid memory key.")

        existing = get_fact(key)

        if existing is None:
            return {
                "success": False,
                "message": f"No memory found for: {key}",
            }

        return {
            "success": False,
            "requires_confirmation": True,
            "action": "forget_fact",
            "key": key,
            "message": f"Confirm deletion of {key}: {existing}",
        }

    raise ValueError(f"Unknown memory tool: {name}")

def commit_memory_action(name: str, arguments: dict) -> dict:
    """
    Execute an authorized memory change.

    IMPORTANT:
    Only call this after authorization or confirmation.
    """

    if name == "remember_fact":
        category = arguments["category"]
        key = arguments["key"]
        value = arguments["value"]

        validate_memory(category, key, value)

        # Check whether we're adding or updating a fact
        existing_record = get_fact_record(key)

        if (
            existing_record is not None
            and existing_record["privacy"] not in CLOUD_ALLOWED_LEVELS
        ):
            return {
                "success": False,
                "action": "blocked",
                "key": key,
                "message": "This memory is restricted from cloud-managed changes.",
            }
        existing = get_fact(key)

        save_fact(category, key, value)

        return {
            "success": True,
            "action": "updated" if existing is not None else "created",
            "key": key,
            "value": value,
        }

    if name == "forget_fact":
        key = arguments["key"]

        if not isinstance(key, str):
            raise ValueError("Invalid memory key.")

        existing_record = get_fact_record(key)

        if (
            existing_record is not None
            and existing_record["privacy"] not in CLOUD_ALLOWED_LEVELS
        ):
            return {
                "success": False,
                "action": "blocked",
                "key": key,
                "message": "This memory is restricted from cloud-managed deletion.",
            }

        deleted = delete_fact(key)

        return {
            "success": deleted,
            "action": "deleted" if deleted else "not_found",
            "key": key,
        }

    raise ValueError(f"Unauthorized memory action: {name}")