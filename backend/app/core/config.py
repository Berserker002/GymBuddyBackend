from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("AI Gym Partner", description="Application name")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/gymbuddy",
        description="Database connection string",
    )

    supabase_jwt_secret: str | None = Field(
        default=None, description="Supabase JWT secret for optional verification"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
