import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ID: str
    REGION: str = "us-central1"
    BUCKET_NAME: str
    GOOGLE_SHEET_ID: str
    SERVICE_ACCOUNT_FILE: str | None = None
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
