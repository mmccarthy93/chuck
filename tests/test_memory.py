import sqlite3

import pytest

from app.memory import facts


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    """Redirect memory operations to a temporary test database."""

    test_db = tmp_path / "test_chuck.db"

    # Redirect the shared database path used by memory functions.
    monkeypatch.setattr(
        facts,
        "DB_PATH",
        str(test_db),
    )

    # Initialize the facts schema.
    facts.initialize_facts()

    return test_db


def test_memory_persists(isolated_database):
    facts.save_fact(
        category="test",
        key="favorite_planet",
        value="Saturn",
    )

    assert facts.get_fact("favorite_planet") == "Saturn"

    # Retrieve the fact through another database connection.
    with sqlite3.connect(isolated_database) as conn:
        row = conn.execute(
            "SELECT value FROM facts WHERE key = ?",
            ("favorite_planet",),
        ).fetchone()

    assert row is not None
    assert row[0] == "Saturn"


def test_restricted_memory_excluded_from_cloud(isolated_database):
    facts.save_fact(
        category="test",
        key="public_preference",
        value="Coffee",
        privacy="general",
    )

    facts.save_fact(
        category="test",
        key="private_preference",
        value="Secret",
        privacy="local_only",
    )

    all_memories = facts.get_all_facts()
    cloud_memories = facts.get_cloud_facts()

    assert len(all_memories) == 2
    assert len(cloud_memories) == 1

    assert "public_preference" in str(cloud_memories)
    assert "private_preference" not in str(cloud_memories)


def test_memory_update_preserves_privacy(isolated_database):
    facts.save_fact(
        category="test",
        key="private_preference",
        value="Original",
        privacy="local_only",
    )

    facts.save_fact(
        category="test",
        key="private_preference",
        value="Updated",
    )

    record = facts.get_fact_record("private_preference")

    assert record is not None
    assert record["value"] == "Updated"
    assert record["privacy"] == "local_only"


def test_sensitive_memory_excluded_from_cloud(isolated_database):
    facts.save_fact(
        category="test",
        key="restricted_test",
        value="Hidden",
        privacy="sensitive",
    )

    assert "restricted_test" not in str(facts.get_cloud_facts())