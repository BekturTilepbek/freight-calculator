from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://freight_user:changeme_local@postgres:5432/freight_db"
    PROJECT_NAME: str = "Freight Calculator API"
    API_V1_PREFIX: str = "/api/v1"

    # JWT
    JWT_SECRET: str = "CHANGE_ME_IN_PROD_super_secret_key_32_chars_min"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 часа


settings = Settings()