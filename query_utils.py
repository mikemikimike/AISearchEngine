from typing import Any, Iterable


def latest_user_query(chat_history: Iterable[dict[str, Any]]) -> str:
    """Return the most recent user message for retrieval."""
    return next(
        (
            message["content"]
            for message in reversed(list(chat_history))
            if message.get("role") == "user"
        ),
        "",
    )
