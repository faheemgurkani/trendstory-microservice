import asyncio
import logging
from trendstory.news_api_loader import NewsAPILoader
from trendstory.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_news_api():
    """Test the NewsAPI directly."""
    loader = NewsAPILoader(settings.NEWS_API_KEY)
    
    # Test with different categories
    categories = ["business", "technology", "entertainment"]
    
    for category in categories:
        logger.info(f"\nTesting category: {category}")
        articles = loader.fetch_news(
            query=category,
            page_size=5,
            sort_by="popularity"
        )
        
        if articles:
            logger.info(f"Got {len(articles)} articles for {category}:")
            for article in articles:
                logger.info(f"Title: {article.get('title')}")
                logger.info(f"Published: {article.get('publishedAt')}")
                logger.info("---")
        else:
            logger.error(f"No articles returned for {category}")

if __name__ == "__main__":
    asyncio.run(test_news_api()) 