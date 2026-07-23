from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Efficiency-V AI Healthcare Companion"
    API_V1_STR: str = "/api/v1"

    # JWT
    SECRET_KEY: str = "efficiency_v_super_secret_jwt_key_change_in_production_32bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Fernet field-level encryption key (32-byte url-safe base64)
    FERNET_ENCRYPTION_KEY: str = "v7bL1_j8R4X-Z9K3mP0qW5tY2uI6oO1aS4dF7gH8jK0="

    # PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "varun2425"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "TetraThon"

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
