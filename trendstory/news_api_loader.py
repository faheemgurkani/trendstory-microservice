import requests
import pandas as pd



class NewsAPILoader:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(self, query, from_date=None, to_date=None, page_size=10, language="en", sort_by="publishedAt"):
        """
        Fetches news articles from NewsAPI based on the given parameters.
        
        Parameters:
            query (str): Search query string (e.g., 'AI', '"Elon Musk"', 'crypto AND bitcoin NOT ethereum').
            from_date (str): Start date for news articles (format: YYYY-MM-DD).
            to_date (str): End date for news articles (format: YYYY-MM-DD).
            page_size (int): Number of articles to retrieve per request (max 100).
            language (str): Language of articles (default: 'en').
            sort_by (str): Sorting order ('relevancy', 'popularity', 'publishedAt').
        
        Returns:
            list: List of retrieved news articles.
        """
        params = {
            "q": query,  # Supports Boolean operators like AND, OR, NOT
            "apiKey": self.api_key,
            "pageSize": page_size,
            "language": language,
            "sortBy": sort_by,
        }
        
        # Handling optional date filters
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        try:
            response = requests.get(self.base_url, params=params)
            
            response.raise_for_status()  # Raising an error for HTTP issues

            data = response.json()

            if data["status"] == "ok":
                return data["articles"]
            else:
                print(f"Error: {data.get('message', 'Unknown error')}")
                
                return None
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            
            return None

    def save_to_csv(self, articles, filename="news_data.csv"):
        """
        Saves news articles to a CSV file.

        Parameters:
            articles (list): List of article dictionaries.
            filename (str): Output CSV filename.
        """

        if len(articles) == 0:
            print("No articles found!")
        
            return

        # Extracting relevant fields
        data = []
        
        for keyword_based_articles in articles:
        
            for article in keyword_based_articles:
                data.append({
                    "Title": article.get("title", ""),
                    "Content": article.get("content", ""),  # Full content if available
                    "Description": article.get("description", ""),
                    "URL": article.get("url", ""),
                    "Source": article["source"]["name"] if article.get("source") else "Unknown",
                    "Published Date": article.get("publishedAt", ""),
                    "Image URL": article.get("urlToImage", ""),
                    "Author": article.get("author", "Unknown"),
                })

        # Converting to DataFrame and save
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        print(f"Data saved to {filename}")
