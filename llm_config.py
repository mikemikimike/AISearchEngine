from pydantic import BaseModel, Field, SecretStr


class GroqLLMConfig(BaseModel):
    model_name: str = Field(..., description="The name of the Groq model to use.")
    temperature: float = Field(0.0, description="The temperature to use for sampling.")
    groq_api_key: SecretStr = Field(..., description="The API key for Groq.")
