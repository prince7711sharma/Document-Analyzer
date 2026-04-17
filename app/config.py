import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # App Settings
    APP_NAME: str = os.getenv("APP_NAME", "Document Analyzer API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    # On Render, use /tmp/uploads (set via env var). Locally defaults to ./temp
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

    # Allowed file types
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf"}


settings = Settings()

# Ensure temp directory exists (works for both local and Render /tmp paths)
os.makedirs(settings.TEMP_DIR, exist_ok=True)