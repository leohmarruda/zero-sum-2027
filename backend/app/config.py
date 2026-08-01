"""Application settings — 12-Factor config via env vars."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py → repo root only
_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _ROOT / ".env"

_DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./dev.db"


def _looks_like_db_url(value: str) -> bool:
    v = value.strip()
    if not v or v.startswith("#"):
        return False
    return "://" in v or v.startswith("sqlite")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    database_url: str = _DEFAULT_DATABASE_URL
    turso_database_url: str = ""
    turso_auth_token: str = ""
    environment: str = "dev"

    @field_validator("database_url", mode="before")
    @classmethod
    def _sanitize_database_url(cls, value: object) -> str:
        if value is None:
            return _DEFAULT_DATABASE_URL
        text = str(value).strip()
        if not _looks_like_db_url(text):
            return _DEFAULT_DATABASE_URL
        return text

    @field_validator("environment", mode="before")
    @classmethod
    def _sanitize_environment(cls, value: object) -> str:
        if value is None:
            return "dev"
        text = str(value).strip().lower()
        if text in {"dev", "prod"}:
            return text
        # Common .env.example mistake: ENVIRONMENT=  # dev | prod
        if not text or text.startswith("#"):
            return "dev"
        return "dev"

    @field_validator("turso_database_url", "turso_auth_token", mode="before")
    @classmethod
    def _blank_comments(cls, value: object) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        if not text or text.startswith("#"):
            return ""
        return text


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    # LiteLLM / llmcall read provider keys from the process environment.
    if settings.openrouter_api_key and not os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
    return settings
