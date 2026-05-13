from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://freight_user:changeme_local@postgres:5432/freight_db"
    PROJECT_NAME: str = "Freight Calculator API"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()