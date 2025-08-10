from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"
    GCP_PROJECT_ID: str = "your-gcp-project-id"
    GCS_BUCKET_NAME: str = "your-gcs-bucket-name"
    LLM_PROVIDER: str = "gemini" # Can be "gemini" or "openai"
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    EXTRACTION_MODEL_NAME: str = "gemini-1.5-flash" # Default for Gemini
    ANALYSIS_MODEL_NAME: str = "gemini-1.5-pro" # Default for Gemini
    # For OpenAI, you might use models like "gpt-3.5-turbo" or "gpt-4o"
    # EXTRACTION_MODEL_NAME_OPENAI: str = "gpt-3.5-turbo"
    # ANALYSIS_MODEL_NAME_OPENAI: str = "gpt-4o"

settings = Settings()
