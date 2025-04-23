"""
TrendStory Microservice

A gRPC service that generates themed stories based on trending topics from various sources.
"""

__version__ = "0.1.0"

from .service import TrendStoryServicer
from .trends_fetcher import TrendsFetcher
from .llm_engine import LLMEngine
from .config import settings

__all__ = ["TrendStoryServicer", "TrendsFetcher", "LLMEngine", "settings"]