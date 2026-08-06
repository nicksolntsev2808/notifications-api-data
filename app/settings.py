from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "notifications-api"
    mongo_uri: str = "mongodb://localhost:28120"
    mongo_db: str = "notificationsdb"
    mongo_collection: str = "notifications"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 9020


settings = Settings()
