from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Trust-Aware Memory Intelligence System"
    DATABASE_URL: str = "sqlite:///./memory_store.db"
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.1-8b-instant"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()

# Force override to avoid rate limit issues on Groq free tier during hackathon presentation
if settings.LLM_MODEL == "llama-3.3-70b-versatile":
    settings.LLM_MODEL = "llama-3.1-8b-instant"
