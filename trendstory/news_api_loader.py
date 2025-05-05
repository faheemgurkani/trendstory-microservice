import requests
import pandas as pd
import logging
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class NewsAPILoader:
    """Class for loading news from NewsAPI."""
    
    def __init__(self, api_key: str):
        """Initialize the loader with API key."""
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        logger.info(f"Initialized NewsAPILoader with API key ending in '...{api_key[-4:]}'")

    def fetch_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        page_size: int = 5,
        language: str = "en",
        sort_by: str = "popularity"
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch news articles from NewsAPI.
        
        Args:
            query: Search query or category (business, entertainment, general, health, science, sports, technology)
            from_date: Start date for articles (YYYY-MM-DDTHH:MM:SSZ)
            page_size: Number of articles to return
            language: Article language
            sort_by: Sort order (relevancy, popularity, publishedAt)
            
        Returns:
            List of articles or None if error
        """
        try:
            # Use top-headlines endpoint
            url = f"{self.base_url}/top-headlines"
            
            # Prepare parameters
            params = {
                "apiKey": self.api_key,
                "pageSize": page_size,
                "language": language
            }
            
            # Check if query is a valid category
            valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
            if query.lower() in valid_categories:
                params["category"] = query.lower()
            else:
                params["q"] = query
            
            # Log request details
            logger.info(f"Making request to NewsAPI - URL: {url}")
            logger.info(f"Request parameters: {params}")
            
            # Make request
            response = requests.get(url, params=params)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # Filter out articles with future dates
                current_time = datetime.now(timezone.utc)
                filtered_articles = []
                future_articles = []
                
                for article in articles:
                    published_at = article.get("publishedAt")
                    if published_at:
                        try:
                            # Parse the date string
                            article_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            
                            # Check if the date is in the future
                            if article_date > current_time:
                                future_articles.append({
                                    'title': article.get('title'),
                                    'date': published_at
                                })
                                continue
                                
                            # Check if the date is too old (more than 1 month)
                            one_month_ago = current_time - timedelta(days=30)
                            if article_date < one_month_ago:
                                logger.warning(f"Filtered out old article: {article.get('title')} with date {published_at}")
                                continue
                                
                            filtered_articles.append(article)
                            
                        except ValueError as e:
                            logger.warning(f"Invalid date format in article: {published_at} - {str(e)}")
                            continue
                
                if future_articles:
                    logger.warning("Found articles with future dates:")
                    for article in future_articles:
                        logger.warning(f"- {article['title']} (date: {article['date']})")
                
                logger.info(f"Successfully fetched {len(filtered_articles)} articles (filtered out {len(articles) - len(filtered_articles)} articles)")
                return filtered_articles
            else:
                logger.error("API Request Failed: %s", response.text)
                logger.error("Request URL: %s", url)
                logger.error("Request params: %s", params)
                logger.error("Error response: %s", response.text)
                return None
                
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return None

    def save_to_csv(self, articles, filename="news_data.csv"):
        """
        Saves news articles to a CSV file.

        Parameters:
            articles (list): List of article dictionaries or list of lists of article dictionaries.
            filename (str): Output CSV filename.
        """
        if not articles:
            logger.warning("No articles to save!")
            return

        # Extracting relevant fields
        data = []
        
        # Check if articles is a list of lists or just a single list
        if isinstance(articles, list) and articles and isinstance(articles[0], list):
            # Handling list of lists
            for keyword_based_articles in articles:
                for article in keyword_based_articles:
                    data.append(self._extract_article_data(article))
        else:
            # Handling single list of articles
            for article in articles:
                data.append(self._extract_article_data(article))

        # Converting to DataFrame and save
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        logger.info(f"Data saved to {filename}")
        
    def _extract_article_data(self, article):
        """Extract relevant data from an article."""
        return {
            "Title": article.get("title", ""),
            "Content": article.get("content", ""),  # Full content if available
            "Description": article.get("description", ""),
            "URL": article.get("url", ""),
            "Source": article["source"]["name"] if article.get("source") else "Unknown",
            "Published Date": article.get("publishedAt", ""),
            "Image URL": article.get("urlToImage", ""),
            "Author": article.get("author", "Unknown"),
        }
