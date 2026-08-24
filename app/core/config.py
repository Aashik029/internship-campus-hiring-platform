from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "development"
    APP_DEBUG: bool = False

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DATABASE_URL: str = ""

    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BCRYPT_ROUNDS: int = 12

    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "Admin"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    def ensure_production_secrets(self) -> None:
        """Fail fast when production runs with placeholder secrets."""
        if self.APP_ENV.lower() == "production" and self.SECRET_KEY == "change-me":
            raise RuntimeError(
                "SECRET_KEY must be set to a strong random value in production "
                "(APP_ENV=production)."
            )


settings = Settings()
