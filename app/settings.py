from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "notifications-api-pg"
    database_url: str = "postgresql+asyncpg://notify_user:notify_pass@localhost:28170/notificationsdb"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 9070


settings = Settings()
