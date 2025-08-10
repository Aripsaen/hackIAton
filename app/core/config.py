from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"
    GCP_PROJECT_ID: str = "your-gcp-project-id"
    GCS_BUCKET_NAME: str = "your-gcs-bucket-name"
    EXTRACTION_LLM_PROVIDER: str = "gemini" # Can be "gemini" or "openai"
    ANALYSIS_LLM_PROVIDER: str = "gemini" # Can be "gemini" or "openai"

    # API Keys for specific models/providers
    EXTRACTION_API_KEY: Optional[str] = None # API Key for the extraction model
    ANALYSIS_API_KEY: Optional[str] = None # API Key for the analysis model

    # Model names. These will be used based on the LLM_PROVIDER setting.
    EXTRACTION_MODEL_NAME: str = "gemini-1.5-flash" # Default for Gemini
    ANALYSIS_MODEL_NAME: str = "gemini-1.5-pro" # Default for Gemini

    # Temperature settings for models
    EXTRACTION_TEMPERATURE: float = 0.1
    ANALYSIS_TEMPERATURE: float = 0.2

    # For OpenAI, you might use models like "gpt-3.5-turbo" or "gpt-4o"
    # EXTRACTION_MODEL_NAME_OPENAI: str = "gpt-3.5-turbo"
    # ANALYSIS_MODEL_NAME_OPENAI: str = "gpt-4o"

settings = Settings()
