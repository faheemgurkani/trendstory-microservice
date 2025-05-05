"""Module for fetching trending topics."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import random

from .news_api_loader import NewsAPILoader
from .config import Settings

logger = logging.getLogger(__name__)

class TrendsFetcher:
    """Class for fetching trending topics from various sources."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the trends fetcher.
        
        Args:
            settings: Application settings containing API keys
        """
        self.settings = settings or Settings()
        logger.info(f"Initializing TrendsFetcher with NEWS_API_KEY ending in '...{self.settings.NEWS_API_KEY[-4:]}'")
        self.news_api_loader = NewsAPILoader(self.settings.NEWS_API_KEY)
        
        # Topic categories for varied searches - using NewsAPI categories
        self.topic_categories = [
            "business", "technology", "science", "health", 
            "entertainment", "sports", "general"
        ]
        
    async def fetch_trends(self, source: str, limit: int = 5) -> List[str]:
        """Fetch trending topics from the specified source.
        
        Args:
            source: The source to fetch trends from ('youtube', 'google', or 'all')
            limit: Maximum number of trends to return
            
        Returns:
            List of trending topics
        """
        logger.info(f"Fetching {limit} trending topics from {source}")
        
        if source == "youtube":
            return await self._fetch_youtube_trends(limit)
        elif source == "google":
            return await self._fetch_google_trends(limit)
        elif source == "all":
            youtube_trends = await self._fetch_youtube_trends(limit // 2)
            google_trends = await self._fetch_google_trends(limit - len(youtube_trends))
            combined_trends = youtube_trends + google_trends
            return combined_trends[:limit]
        else:
            logger.warning(f"Unknown source: {source}, falling back to Google trends")
            return await self._fetch_google_trends(limit)
            
    async def _fetch_youtube_trends(self, limit: int) -> List[str]:
        """Fetch trending topics from YouTube."""
        try:
            # Select random categories for diversity
            categories = random.sample(self.topic_categories, min(3, len(self.topic_categories)))
            logger.info(f"Selected categories for YouTube trends: {categories}")
            
            all_trends = []
            for category in categories:
                # Run in executor to prevent blocking
                loop = asyncio.get_event_loop()
                
                logger.info(f"Making NewsAPI request for category '{category}'")
                articles = await loop.run_in_executor(
                    None, 
                    lambda: self.news_api_loader.fetch_news(
                        query=category,
                        page_size=5,
                        sort_by="popularity"
                    )
                )
                
                if articles is None:
                    logger.error(f"NewsAPI request failed for category '{category}'")
                    continue
                    
                logger.info(f"NewsAPI response for category '{category}': {articles}")
                
                if articles:
                    # Extract titles as trends and filter out unwanted topics
                    trends = []
                    for article in articles:
                        title = article.get('title', '')
                        if not title:
                            continue
                            
                        # Skip articles with future dates
                        published_at = article.get('publishedAt')
                        if published_at:
                            try:
                                article_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                if article_date > datetime.now(timezone.utc):
                                    logger.warning(f"Skipping future article: {title}")
                                    continue
                            except ValueError:
                                logger.warning(f"Invalid date format: {published_at}")
                                continue
                        
                        # Skip articles with specific unwanted phrases
                        if any(phrase in title.lower() for phrase in [
                            "gold house", "nasdaq", "power summit", "a100",
                            "mike waltz", "left the chat", "night court",
                            "season 3", "daily litg"
                        ]):
                            logger.warning(f"Skipping unwanted article: {title}")
                            continue
                            
                        trends.append(title)
                        
                    logger.info(f"Fetched {len(trends)} trends for category '{category}'")
                    all_trends.extend(trends)
                else:
                    logger.warning(f"No articles returned for category '{category}'")
            
            # Deduplicate and limit
            unique_trends = list(dict.fromkeys(all_trends))
            logger.info(f"Fetched {len(unique_trends)} unique YouTube trends")
            
            if not unique_trends:
                logger.error("API failed - no trends fetched")
                return []
            
            return unique_trends[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching YouTube trends: {str(e)}")
            logger.error("API failed due to error")
            return []
            
    async def _fetch_google_trends(self, limit: int) -> List[str]:
        """Fetch trending topics from Google News."""
        try:
            # Select random categories for diversity
            categories = random.sample(self.topic_categories, min(3, len(self.topic_categories)))
            logger.info(f"Selected categories for Google trends: {categories}")
            
            all_trends = []
            for category in categories:
                # Run in executor to prevent blocking
                loop = asyncio.get_event_loop()
                
                logger.info(f"Making NewsAPI request for category '{category}'")
                articles = await loop.run_in_executor(
                    None, 
                    lambda: self.news_api_loader.fetch_news(
                        query=category,
                        page_size=5,
                        sort_by="relevancy"
                    )
                )
                
                if articles is None:
                    logger.error(f"NewsAPI request failed for category '{category}'")
                    continue
                    
                logger.info(f"NewsAPI response for category '{category}': {articles}")
                
                if articles:
                    # Extract titles as trends and filter out unwanted topics
                    trends = []
                    for article in articles:
                        title = article.get('title', '')
                        if not title:
                            continue
                            
                        # Skip articles with future dates
                        published_at = article.get('publishedAt')
                        if published_at:
                            try:
                                article_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                if article_date > datetime.now(timezone.utc):
                                    logger.warning(f"Skipping future article: {title}")
                                    continue
                            except ValueError:
                                logger.warning(f"Invalid date format: {published_at}")
                                continue
                        
                        # Skip articles with specific unwanted phrases
                        if any(phrase in title.lower() for phrase in [
                            "gold house", "nasdaq", "power summit", "a100",
                            "mike waltz", "left the chat", "night court",
                            "season 3", "daily litg"
                        ]):
                            logger.warning(f"Skipping unwanted article: {title}")
                            continue
                            
                        trends.append(title)
                        
                    logger.info(f"Fetched {len(trends)} trends for category '{category}'")
                    all_trends.extend(trends)
                else:
                    logger.warning(f"No articles returned for category '{category}'")
            
            # Deduplicate and limit
            unique_trends = list(dict.fromkeys(all_trends))
            logger.info(f"Fetched {len(unique_trends)} unique Google trends")
            
            if not unique_trends:
                logger.error("API failed - no trends fetched")
                return []
            
            return unique_trends[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching Google trends: {str(e)}")
            logger.error("API failed due to error")
            return []
    
    def _get_fallback_trends(self, limit: int) -> List[str]:
        """Get fallback trends in case API calls fail."""
        logger.warning("Using fallback trends due to API issues")
        
        fallback_trends = [
            "Latest developments in artificial intelligence",
            "Climate change mitigation strategies",
            "Global economic outlook for 2025",
            "Advancements in renewable energy technology",
            "Space exploration milestones",
            "Healthcare innovation and medical breakthroughs",
            "Cybersecurity challenges and solutions",
            "Digital transformation in business",
            "Sustainable development initiatives",
            "Geopolitical shifts and international relations"
        ]
        
        return fallback_trends[:limit]
