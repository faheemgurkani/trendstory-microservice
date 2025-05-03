# """Module for fetching trending topics from YouTube and Google Trends."""

# import logging
# import asyncio
# from typing import List, Dict, Any
# from datetime import datetime, timedelta
# import aiohttp
# from pytrends.request import TrendReq

# from .config import settings

# logger = logging.getLogger(__name__)

# class TrendsFetcher:
#     """Class for fetching trending topics from various sources."""
    
#     def __init__(self):
#         """Initialize the trends fetcher."""
#         self.youtube_api_key = settings.YOUTUBE_API_KEY
#         self.pytrends = TrendReq(hl='en-US', tz=360)
        
#     async def fetch_trends(self, source: str, limit: int = 5) -> List[str]:
#         """Fetch trending topics from the specified source.
        
#         Args:
#             source: The source to fetch trends from ('youtube' or 'google')
#             limit: Maximum number of trends to return
            
#         Returns:
#             List of trending topics
#         """
#         if source.lower() == 'youtube':
#             return await self._fetch_youtube_trends(limit)
#         elif source.lower() == 'google':
#             return await self._fetch_google_trends(limit)
#         else:
#             raise ValueError(f"Unsupported trend source: {source}")
            
#     async def _fetch_youtube_trends(self, limit: int) -> List[str]:
#         """Fetch trending topics from YouTube."""
#         try:
#             logger.info("\n\nFetching YouTube trends...\n")
            
#             # Use mock data for now
#             mock_trends = [
#                 "Climate change affecting coastal cities",
#                 "NASA's new space telescope discoveries",
#                 "Top 10 upcoming video games in 2025",
#                 "Latest smartphone innovations",
#                 "Sustainable fashion trends"
#             ]
            
#             logger.info(f"\n\nYouTube trends fetched: {mock_trends[:limit]}\n")
#             return mock_trends[:limit]
            
#         except Exception as e:
#             logger.error(f"\n\nError fetching YouTube trends: {str(e)}\n")
#             raise RuntimeError(f"Failed to fetch YouTube trends: {str(e)}")
            
#     async def _fetch_google_trends(self, limit: int) -> List[str]:
#         """Fetch trending topics from Google Trends."""
#         try:
#             logger.info("\n\nFetching Google trends...\n")
            
#             # Use mock data for now
#             mock_trends = [
#                 "Celebrity news",
#                 "Health and wellness tips",
#                 "Latest tech innovations",
#                 "Travel destinations 2025",
#                 "Home improvement ideas"
#             ]
            
#             logger.info(f"\n\nGoogle trends fetched: {mock_trends[:limit]}\n")
#             return mock_trends[:limit]
            
#         except Exception as e:
#             logger.error(f"\n\nError fetching Google Trends: {str(e)}\n")
#             raise RuntimeError(f"Failed to fetch Google Trends: {str(e)}")
            
#     async def _get_mock_google_trends(self, limit: int) -> List[str]:
#         """Get mock Google trends data."""
#         try:
#             logger.info("\n\nGetting mock Google trends data...\n")
            
#             mock_trends = [
#                 "Celebrity news",
#                 "Health and wellness tips",
#                 "Latest tech innovations",
#                 "Travel destinations 2025",
#                 "Home improvement ideas"
#             ]
            
#             logger.info(f"\n\nMock Google trends fetched: {mock_trends[:limit]}\n")
#             return mock_trends[:limit]
            
#         except Exception as e:
#             logger.error(f"\n\nError getting mock Google trends: {str(e)}\n")
#             raise RuntimeError(f"Failed to get mock Google trends: {str(e)}")



import logging
import asyncio
from datetime import datetime, timedelta
from typing import List

from .config import settings
from .news_api_loader import NewsAPILoader

logger = logging.getLogger(__name__)



class TrendsFetcher:
    """Class for fetching 'trending' topics via NewsAPI articles."""

    def __init__(self):
        """Initialize the trends fetcher."""
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.news_loader = NewsAPILoader(settings.NEWS_API_KEY)

    async def fetch_trends(self, source: str, limit: int = 5) -> List[str]:
        """
        Fetch trending topics from the specified source:
        'youtube', 'google', or 'news'.
        """
        source = source.lower()

        if source in ('youtube', 'google', 'news'):
            return await self._fetch_news_titles(source, limit)
        else:
            raise ValueError(f"Unsupported trend source: {source}")

    async def _fetch_news_titles(self, source: str, limit: int) -> List[str]:
        """
        Query NewsAPI for the latest articles based on the source
        and return their titles.
        """
        if source == "youtube":
            query = "YouTube Trending Topics"
        elif source == "google":
            query = "Google Trending Topics"
        else:  # for 'news'
            query = "Technology"  # or any other general-purpose topic

        from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        loop = asyncio.get_running_loop()

        try:
            articles = await loop.run_in_executor(
                None,
                self.news_loader.fetch_news,
                query,
                from_date,
                None,
                limit,
                "en",
                "publishedAt"
            )
        except Exception as e:
            logger.error(f"Error fetching news trends for {source}: {e}")

            return []

        if not articles:
            return []

        titles = [a.get("title", "").strip() for a in articles]

        logger.info(f"Fetched {len(titles)} '{source}' news titles: {titles}")

        return titles[:limit]

async def main():
    fetcher = TrendsFetcher()

    print("\nFetching YouTube trends...\n")

    youtube_trends = await fetcher.fetch_trends("youtube", limit=5)

    print("YouTube Trends:")

    for trend in youtube_trends:
        print(f"- {trend}")

    print("\nFetching Google trends...\n")

    google_trends = await fetcher.fetch_trends("google", limit=5)

    print("Google Trends:")

    for trend in google_trends:
        print(f"- {trend}")

    print("\nFetching General News trends...\n")

    news_trends = await fetcher.fetch_trends("news", limit=5)

    print("News Trends:")

    for trend in news_trends:
        print(f"- {trend}")



if __name__ == "__main__":
    asyncio.run(main())
