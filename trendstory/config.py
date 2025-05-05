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
    NEWS_API_KEY: Optional[str] = "2041b0a1ad3f4118bad3d68751263fc2"
    
    # Google Trends settings
    GOOGLE_TRENDS_REGION: str = "united_states"
    GOOGLE_TRENDS_LANGUAGE: str = "en-US"
    GOOGLE_TRENDS_TIMEZONE: int = 360  # UTC-6
    
    # LLM settings
    MODEL_NAME: str = "dolphin3:latest"
    OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    MODEL_CACHE_DIR: str = "./model_cache"
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    
    # Trends settings
    DEFAULT_TRENDS_LIMIT: int = 5
    SUPPORTED_SOURCES: List[str] = ["youtube", "google"]
    SUPPORTED_THEMES: List[str] = ["comedy", "tragedy", "sarcasm", "mystery", "romance", "sci-fi"]
    
    # Default prompt templates
    PROMPT_TEMPLATES: Dict[str, str] = {
        "default": "Create a short story incorporating the following current trending topics: {topics}. Make it {theme} themed. Use only current events and avoid any future dates or predictions.",
        "comedy": "Write a humorous and lighthearted story that includes these current trending topics: {topics}. Make it funny and witty, but stick to current events only.",
        "tragedy": "Write a sad and emotional story that incorporates these current trending topics: {topics}. Focus on loss and difficult emotions, using only present-day events.",
        "sarcasm": "Write a sarcastic and ironic story that makes fun of these current trending topics: {topics}. Don't hold back on the cynicism, but keep it grounded in present reality.",
        "mystery": "Write a suspenseful mystery story that weaves in these current trending topics: {topics}. Include a twist ending if possible, but avoid any future dates or predictions.",
        "romance": "Write a romantic story that incorporates these current trending topics: {topics}. Focus on the relationship between characters in present-day settings.",
        "sci-fi": "Write a science fiction story that references these current trending topics: {topics}. While it can be futuristic, avoid specific future dates and keep it grounded in current technology trends."
    }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Create settings instance
settings = Settings()