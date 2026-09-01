"""
Application configuration.

Loads settings from environment variables / a local .env file.
Never hardcode secrets here - everything sensitive comes from the environment.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Course Builder"
    ENVIRONMENT: str = "development"

    # --- Database ---
    DATABASE_URL: str

    # --- Auth ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- CORS ---
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # --- AI (wired up starting Phase 3) ---
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # When true (or when OPENAI_API_KEY is unset), agents use a deterministic
    # local generator instead of calling the OpenAI API. Useful for local
    # development and for running the test suite without burning API credits.
    USE_MOCK_AI: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we only parse the environment once."""
    return Settings()


settings = get_settings()
