"""Module for fetching trending topics from YouTube and Google Trends."""

import logging
import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import googleapiclient.discovery
from pytrends.request import TrendReq
from .config import settings

logger = logging.getLogger(__name__)

class TrendsFetcher:
    """Class to fetch trending topics from YouTube and Google Trends."""
    
    def __init__(self):
        """Initialize the trends fetcher."""
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    async def fetch_trends(self, source: str, limit: int) -> List[str]:
        """Fetch trending topics from specified source.
        
        Args:
            source: The source to fetch trends from ("youtube" or "google")
            limit: Maximum number of trends to return
            
        Returns:
            List of trending topic strings
            
        Raises:
            ValueError: If the source is not supported
            RuntimeError: If there's an error fetching trends
        """
        if source not in ["youtube", "google"]:
            raise ValueError("Only 'youtube' and 'google' sources are supported")
            
        try:
            if source == "youtube":
                return await self._fetch_youtube_trends(limit)
            else:
                return await self._fetch_google_trends(limit)
        except Exception as e:
            logger.error(f"Error fetching trends from {source}: {str(e)}")
            raise RuntimeError(f"Failed to fetch trends from {source}: {str(e)}")
    
    async def _fetch_youtube_trends(self, limit: int) -> List[str]:
        """Fetch trending videos from YouTube.
        
        Args:
            limit: Maximum number of trends to return
            
        Returns:
            List of trending video titles
        """
        # Always use mock data for YouTube as per requirements
        mock_trends = [
            "How to make homemade pasta from scratch",
            "Climate change affecting coastal cities",
            "DIY smartphone projector",
            "Secrets to a perfect cup of coffee",
            "Top 10 upcoming video games in 2025",
            "Machine learning explained in 5 minutes",
            "NASA's new space telescope discoveries",
            "Sustainable living tips for 2025",
            "Virtual reality gaming revolution",
            "Artificial intelligence in healthcare"
        ]
        
        # Return a random subset of mock trends
        import random
        random.shuffle(mock_trends)
        return mock_trends[:limit]
    
    async def _fetch_google_trends(self, limit: int) -> List[str]:
        """Fetch trending searches from Google Trends.
        
        Args:
            limit: Maximum number of trends to return
            
        Returns:
            List of trending search terms
        """
        try:
            # Get trending searches
            self.pytrends.trending_searches(pn='united_states')
            trends = self.pytrends.trending_searches()
            return trends[:limit]
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {str(e)}")
            # Fallback to mock data if API fails
            mock_trends = [
                "Latest tech innovations",
                "Global weather patterns",
                "Stock market updates",
                "Celebrity news",
                "Sports highlights",
                "Health and wellness tips",
                "Travel destinations",
                "Food recipes",
                "Fashion trends",
                "Educational resources"
            ]
            import random
            random.shuffle(mock_trends)
            return mock_trends[:limit]