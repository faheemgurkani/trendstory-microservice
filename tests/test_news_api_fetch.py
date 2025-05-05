import requests
from datetime import datetime, timedelta, timezone



class NewsAPILoader:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(self, query, from_date=None, to_date=None, page_size=5, language="en", sort_by="publishedAt"):
        params = {
            "q": query,
            "apiKey": self.api_key,
            "pageSize": page_size,
            "language": language,
            "sortBy": sort_by,
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # print("\nFull response JSON:\n", data)

            if data["status"] == "ok":
                return data["articles"]
            else:
                print(f"Error: {data.get('message', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            
            return None



if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()  
    
    #API_KEY = os.getenv("NEWS_API_KEY")
    API_KEY = "2041b0a1ad3f4118bad3d68751263fc2"
    # print(f"API_KEY: {API_KEY}")  # For, testing

    # Query and date range for last 24 hours
    query = "AI"
    # from_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    loader = NewsAPILoader(API_KEY)

    articles = loader.fetch_news(query=query, from_date=from_date, page_size=5)

    if articles:
        print(f"\nFetched {len(articles)} articles for query: '{query}'\n")
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article.get('title', 'No title')}")
            print(f"   Published at: {article.get('publishedAt', 'N/A')}")
            print(f"   Source: {article['source']['name']}\n")
    else:
        print("\nNo articles returned.")
