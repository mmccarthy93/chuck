import sqlite3
from datetime import datetime, timezone

from app.memory.database import DB_PATH

PRIVACY_LEVELS = {
    "general",
    "personal",
    "local_only",
    "sensitive",
}

CLOUD_ALLOWED_LEVELS = {"general", "personal"}

def initialize_facts():
    """Initialize and migrate the persistent fact database."""

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                privacy TEXT NOT NULL DEFAULT 'personal',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Check the existing database schema.
        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(facts)")
        }

        # Safely migrate databases created before privacy existed.
        if "privacy" not in columns:
            conn.execute("""
                ALTER TABLE facts
                ADD COLUMN privacy TEXT NOT NULL DEFAULT 'personal'
            """)


def save_fact(
    category: str,
    key: str,
    value: str,
    privacy: str | None = None
):
    """Save or update a fact while preserving privacy settings."""

    if privacy is not None and privacy not in PRIVACY_LEVELS:
        raise ValueError(f"Invalid privacy level: {privacy}")

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO facts (
                category, key, value, privacy,
                created_at, updated_at
            )
            VALUES (?, ?, ?, COALESCE(?, 'personal'), ?, ?)

            ON CONFLICT(key) DO UPDATE SET
                category = excluded.category,
                value = excluded.value,
                privacy = COALESCE(?, facts.privacy),
                updated_at = excluded.updated_at
        """, (
            category,
            key,
            value,
            privacy,
            now,
            now,
            privacy,
        ))


def get_fact(key: str):
    """Retrieve a fact by its unique key."""

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT value FROM facts WHERE key = ?",
            (key,)
        ).fetchone()

    return row[0] if row else None


def get_all_facts():
    """Retrieve saved facts including their privacy classifications."""

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT category, key, value, privacy
            FROM facts
            ORDER BY category, key
        """).fetchall()

    return [
        {
            "category": category,
            "key": key,
            "value": value,
            "privacy": privacy,
        }
        for category, key, value, privacy in rows
    ]


def delete_fact(key: str):
    """Remove a saved fact."""

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM facts WHERE key = ?",
            (key,)
        )

    return cursor.rowcount > 0

def get_cloud_facts():
    """Return only facts permitted to reach cloud models."""

    with sqlite3.connect(DB_PATH) as conn:
        placeholders = ",".join(
            "?" for _ in CLOUD_ALLOWED_LEVELS
        )

        rows = conn.execute(
            f"""
            SELECT category, key, value, privacy
            FROM facts
            WHERE privacy IN ({placeholders})
            ORDER BY category, key
            """,
            tuple(CLOUD_ALLOWED_LEVELS),
        ).fetchall()

    return [
        {
            "category": category,
            "key": key,
            "value": value,
            "privacy": privacy,
        }
        for category, key, value, privacy in rows
    ]

def get_fact_record(key: str):
    """Retrieve a complete memory record, including privacy."""

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT category, key, value, privacy
            FROM facts
            WHERE key = ?
            """,
            (key,)
        ).fetchone()

    if row is None:
        return None

    return {
        "category": row[0],
        "key": row[1],
        "value": row[2],
        "privacy": row[3],
    }