"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    APP_NAME: str = "Taskly API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://taskly:taskly@postgres:5432/taskly"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000"

    # Email (SendGrid or SMTP)
    SENDGRID_API_KEY: str = ""
    SMTP_HOST: str = "mailhog"  # Default to MailHog for local dev
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ""  # MailHog doesn't need auth
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@taskly.app"
    FROM_NAME: str = "Taskly"
    APP_URL: str = "http://localhost:3000"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse CORS_ORIGINS from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]


settings = Settings()
