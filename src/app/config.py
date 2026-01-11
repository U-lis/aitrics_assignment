from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    AES_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # ty: ignore[missing-argument]
