from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "SaveBud"
    api_v1_prefix: str = "/api/v1"
    app_env: str = "development"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+asyncpg://finance:finance@postgres:5432/finance_db"
    redis_url: str = "redis://redis:6379/0"
    model_dir: str = str(Path(__file__).resolve().parents[2] / "ml" / "artifacts")
    seed_dataset_path: str = str(Path(__file__).resolve().parents[2] / "ml" / "data" / "monthly_spending_dataset_2020_2025.csv")
    cors_origins_raw: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=(),
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if normalized.startswith("postgres://"):
            normalized = normalized.replace("postgres://", "postgresql+asyncpg://", 1)
        elif normalized.startswith("postgresql://"):
            normalized = normalized.replace("postgresql://", "postgresql+asyncpg://", 1)

        if "asyncpg" not in normalized:
            return normalized

        parts = urlsplit(normalized)
        query_pairs = []
        has_sslmode = False
        for key, item in parse_qsl(parts.query, keep_blank_values=True):
            if key == "channel_binding":
                continue
            if key == "sslmode":
                has_sslmode = True
            query_pairs.append((key, item))

        if not has_sslmode:
            query_pairs.append(("sslmode", "require"))

        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query_pairs), parts.fragment))

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
