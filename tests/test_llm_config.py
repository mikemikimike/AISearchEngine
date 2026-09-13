from llm_config import GroqLLMConfig


def test_groq_api_key_is_masked_when_config_is_serialized():
    secret = "gsk-production-secret"
    config = GroqLLMConfig(model_name="llama3", groq_api_key=secret)

    assert config.groq_api_key.get_secret_value() == secret
    assert secret not in repr(config.model_dump())
    assert secret not in config.model_dump_json()
    assert str(config.groq_api_key) == "**********"
