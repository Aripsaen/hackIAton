import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ID: str
    REGION: str = "us-central1"
    BUCKET_NAME: str
    GOOGLE_SHEET_ID: str
    SERVICE_ACCOUNT_FILE: str | None = None
    
    # LLM Settings
    LLM_PROVIDER: str = "vertex"
    VERTEX_MODEL_NAME: str = "gemini-1.5-flash-001"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
