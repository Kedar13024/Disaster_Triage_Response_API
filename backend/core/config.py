"""Application settings loaded from environment variables and the .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Define required database and token settings for the API."""
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str
    secret_key : str
    algorithm : str
    access_token_minutes : int

    @property
    def database_pass(self) -> str:
        """Keep existing database URL callers compatible."""
        return self.database_password

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings()->Settings:
    """Return the cached application settings instance."""
    return Settings()
