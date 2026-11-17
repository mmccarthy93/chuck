import re

from app.memory.facts import get_cloud_facts


STOP_WORDS = {
    "the", "and", "for", "you", "your", "what",
    "with", "that", "this", "have", "about",
    "from", "would", "could", "should", "chuck",
    "please", "tell", "some", "into", "give",
}


def tokenize(text: str) -> set[str]:
    """Extract meaningful words from text."""

    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def retrieve_relevant_facts(
    query: str,
    limit: int = 5
) -> list[dict]:
    """Retrieve cloud-eligible facts relevant to the query."""

    query_words = tokenize(query)

    if not query_words:
        return []

    scored = []

    for fact in get_cloud_facts():
        searchable = (
            fact["category"] + " "
            + fact["key"].replace("_", " ")
            + fact["value"]
        )

        fact_words = tokenize(searchable)
        score = len(query_words.intersection(fact_words))

        if score > 0:
            scored.append((score, fact))

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        fact for _, fact in scored[:limit]
    ]