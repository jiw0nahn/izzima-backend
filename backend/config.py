from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase / Postgres (pgvector)
    supabase_url: str = ""
    supabase_key: str = ""
    database_url: str = ""

    # AI Pipeline service (separate app, called over HTTP)
    ai_pipeline_url: str = "http://localhost:8100"


settings = Settings()
