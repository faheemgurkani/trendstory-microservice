"""Module for fetching trending topics from YouTube and Google Trends."""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
import aiohttp
from pytrends.request import TrendReq

from .config import settings

logger = logging.getLogger(__name__)

class TrendsFetcher:
    """Class for fetching trending topics from various sources."""
    
    def __init__(self):
        """Initialize the trends fetcher."""
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    async def fetch_trends(self, source: str, limit: int = 5) -> List[str]:
        """Fetch trending topics from the specified source.
        
        Args:
            source: The source to fetch trends from ('youtube' or 'google')
            limit: Maximum number of trends to return
            
        Returns:
            List of trending topics
        """
        if source.lower() == 'youtube':
            return await self._fetch_youtube_trends(limit)
        elif source.lower() == 'google':
            return await self._fetch_google_trends(limit)
        else:
            raise ValueError(f"Unsupported trend source: {source}")
            
    async def _fetch_youtube_trends(self, limit: int) -> List[str]:
        """Fetch trending topics from YouTube."""
        try:
            logger.info("\n\nFetching YouTube trends...\n")
            
            # Use mock data for now
            mock_trends = [
                "Climate change affecting coastal cities",
                "NASA's new space telescope discoveries",
                "Top 10 upcoming video games in 2025",
                "Latest smartphone innovations",
                "Sustainable fashion trends"
            ]
            
            logger.info(f"\n\nYouTube trends fetched: {mock_trends[:limit]}\n")
            return mock_trends[:limit]
            
        except Exception as e:
            logger.error(f"\n\nError fetching YouTube trends: {str(e)}\n")
            raise RuntimeError(f"Failed to fetch YouTube trends: {str(e)}")
            
    async def _fetch_google_trends(self, limit: int) -> List[str]:
        """Fetch trending topics from Google Trends."""
        try:
            logger.info("\n\nFetching Google trends...\n")
            
            # Use mock data for now
            mock_trends = [
                "Celebrity news",
                "Health and wellness tips",
                "Latest tech innovations",
                "Travel destinations 2025",
                "Home improvement ideas"
            ]
            
            logger.info(f"\n\nGoogle trends fetched: {mock_trends[:limit]}\n")
            return mock_trends[:limit]
            
        except Exception as e:
            logger.error(f"\n\nError fetching Google Trends: {str(e)}\n")
            raise RuntimeError(f"Failed to fetch Google Trends: {str(e)}")
            
    async def _get_mock_google_trends(self, limit: int) -> List[str]:
        """Get mock Google trends data."""
        try:
            logger.info("\n\nGetting mock Google trends data...\n")
            
            mock_trends = [
                "Celebrity news",
                "Health and wellness tips",
                "Latest tech innovations",
                "Travel destinations 2025",
                "Home improvement ideas"
            ]
            
            logger.info(f"\n\nMock Google trends fetched: {mock_trends[:limit]}\n")
            return mock_trends[:limit]
            
        except Exception as e:
            logger.error(f"\n\nError getting mock Google trends: {str(e)}\n")
            raise RuntimeError(f"Failed to get mock Google trends: {str(e)}")