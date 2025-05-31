from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = "GSE Backend"
    API_V1_STR: str = "/api/v1"
    
    # JWT settings
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost/gse2"
    
    # Initial admin credentials
    INITIAL_ADMIN_EMAIL: str
    INITIAL_ADMIN_PASSWORD: str

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    # Base directory for file operations (e.g., uploads)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

# Instantiate settings
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True)

# Log settings initialization
logger.info("Settings initialized with project name: %s", settings.PROJECT_NAME)