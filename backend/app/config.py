from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/content_agent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # LLM
    llm_provider: str = "openai"   # "openai" or "anthropic"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
