"""Unit tests for the Trends Fetcher (NewsAPI-based)."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from trendstory.trends_fetcher import TrendsFetcher

@pytest.fixture
def fetcher():
    return TrendsFetcher()

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news")
async def test_fetch_youtube_trends_success(mock_fetch_news, fetcher):
    mock_fetch_news.return_value = [
        {"title": "Trend 1", "publishedAt": "2024-01-01T00:00:00Z"},
        {"title": "Trend 2", "publishedAt": "2024-01-01T00:00:00Z"}
    ]
    trends = await fetcher.fetch_trends("youtube", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 2
    for topic in trends:
        assert isinstance(topic, str)
        assert topic

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news")
async def test_fetch_google_trends_success(mock_fetch_news, fetcher):
    mock_fetch_news.return_value = [
        {"title": "Google Trend 1", "publishedAt": "2024-01-01T00:00:00Z"},
        {"title": "Google Trend 2", "publishedAt": "2024-01-01T00:00:00Z"}
    ]
    trends = await fetcher.fetch_trends("google", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 2
    for topic in trends:
        assert isinstance(topic, str)
        assert topic

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news")
async def test_fetch_trends_all_source(mock_fetch_news, fetcher):
    # Simulate different results for youtube and google
    def side_effect(query, page_size, sort_by):
        if sort_by == "popularity":
            return [
                {"title": "YT Trend 1", "publishedAt": "2024-01-01T00:00:00Z"}
            ]
        else:
            return [
                {"title": "G Trend 1", "publishedAt": "2024-01-01T00:00:00Z"}
            ]
    mock_fetch_news.side_effect = side_effect
    trends = await fetcher.fetch_trends("all", limit=2)
    assert len(trends) == 2
    assert any("YT Trend 1" in t or "G Trend 1" in t for t in trends)

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news", return_value=None)
async def test_fetch_youtube_trends_empty(mock_fetch_news, fetcher):
    trends = await fetcher.fetch_trends("youtube", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 0

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news", side_effect=Exception("API Error"))
async def test_fetch_youtube_trends_error(mock_fetch_news, fetcher):
    trends = await fetcher.fetch_trends("youtube", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 0

@pytest.mark.asyncio
@patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news", side_effect=Exception("API Error"))
async def test_fetch_google_trends_error(mock_fetch_news, fetcher):
    trends = await fetcher.fetch_trends("google", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 0

def test_get_fallback_trends(fetcher):
    fallback = fetcher._get_fallback_trends(3)
    assert isinstance(fallback, list)
    assert len(fallback) == 3
    for topic in fallback:
        assert isinstance(topic, str)
        assert topic

@pytest.mark.asyncio
async def test_invalid_source_fallback(fetcher):
    # Should fallback to google trends, not raise
    with patch("trendstory.trends_fetcher.NewsAPILoader.fetch_news", return_value=[{"title": "Fallback", "publishedAt": "2024-01-01T00:00:00Z"}]):
        trends = await fetcher.fetch_trends("invalid_source", limit=1)
        assert isinstance(trends, list)
        assert len(trends) == 1
        assert trends[0] == "Fallback"