from query_utils import latest_user_query


def test_retrieval_uses_latest_user_question_after_assistant_reply():
    history = [
        {"role": "user", "content": "What is FAISS?"},
        {"role": "assistant", "content": "A vector index."},
        {"role": "user", "content": "How does it rank results?"},
    ]

    assert latest_user_query(history) == "How does it rank results?"


def test_retrieval_ignores_assistant_messages_after_latest_question():
    history = [
        {"role": "user", "content": "Explain embeddings."},
        {"role": "assistant", "content": "An explanation."},
    ]

    assert latest_user_query(history) == "Explain embeddings."


def test_retrieval_returns_empty_query_without_user_message():
    assert latest_user_query([{"role": "assistant", "content": "Hello"}]) == ""
