"""Configuration module for TrendStory microservice."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any, Optional, List

class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 50051
    DEBUG: bool = False
    
    # API Keys
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Google Trends settings
    GOOGLE_TRENDS_REGION: str = "united_states"
    GOOGLE_TRENDS_LANGUAGE: str = "en-US"
    GOOGLE_TRENDS_TIMEZONE: int = 360  # UTC-6
    
    # LLM settings
    MODEL_NAME: str = "t5-small"
    MODEL_CACHE_DIR: str = "./model_cache"
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    
    # Trends settings
    DEFAULT_TRENDS_LIMIT: int = 5
    SUPPORTED_SOURCES: List[str] = ["youtube", "google"]
    SUPPORTED_THEMES: List[str] = ["comedy", "tragedy", "sarcasm", "mystery", "romance", "sci-fi"]
    
    # Default prompt templates
    PROMPT_TEMPLATES: Dict[str, str] = {
        "default": "Create a short story incorporating the following trending topics: {topics}. Make it {theme} themed.",
        "comedy": "Write a humorous and lighthearted story that includes these trending topics: {topics}. Make it funny and witty.",
        "tragedy": "Write a sad and emotional story that incorporates these trending topics: {topics}. Focus on loss and difficult emotions.",
        "sarcasm": "Write a sarcastic and ironic story that makes fun of these trending topics: {topics}. Don't hold back on the cynicism.",
        "mystery": "Write a suspenseful mystery story that weaves in these trending topics: {topics}. Include a twist ending if possible.",
        "romance": "Write a romantic story that incorporates these trending topics: {topics}. Focus on the relationship between characters.",
        "sci-fi": "Write a science fiction story set in the future that references these trending topics: {topics}. Include futuristic technology."
    }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Create settings instance
settings = Settings()