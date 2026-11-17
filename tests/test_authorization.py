import pytest

from app.memory.authorization import (
    is_explicit_memory_command,
    is_explicit_memory_recall,
    is_memory_question,
)


@pytest.mark.parametrize(
    "message,action,expected",
    [
        ("Remember my favorite drink is Diet Coke.", "remember_fact", True),
        ("Forget my favorite drink.", "forget_fact", True),
        ("My favorite drink is Diet Coke.", "remember_fact", False),
        ("What's my favorite drink?", "remember_fact", False),
    ],
)
def test_memory_write_authorization(message, action, expected):
    assert is_explicit_memory_command(message, action) == expected


@pytest.mark.parametrize(
    "message,expected",
    [
        ("List everything you remember about me.", True),
        ("What's my favorite drink?", False),
        ("Hello Chuck.", False),
    ],
)
def test_explicit_memory_recall(message, expected):
    assert is_explicit_memory_recall(message) == expected


@pytest.mark.parametrize(
    "message,expected",
    [
        ("What's my favorite drink?", True),
        ("What is my favorite movie?", True),
        ("Remember my favorite drink.", False),
    ],
)
def test_memory_questions(message, expected):
    assert is_memory_question(message) == expected