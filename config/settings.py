"""Central config, loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 4

    confidence_threshold: float = 0.70

    db_path: str = "data/careguard.db"
    index_path: str = "data/index"


settings = Settings()