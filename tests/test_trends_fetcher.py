"""Unit tests for the Trends Fetcher."""

import pytest
from unittest.mock import patch, MagicMock
from pytrends.request import TrendReq

from trendstory.trends_fetcher import TrendsFetcher

@pytest.fixture
def fetcher():
    return TrendsFetcher()

@pytest.mark.asyncio
async def test_fetch_youtube_trends(fetcher):
    """Test fetching YouTube trends."""
    # Call fetch_trends and verify it returns a list of strings of specified length
    trends = await fetcher.fetch_trends("youtube", limit=2)
    assert isinstance(trends, list)
    assert len(trends) == 2
    # Each trend should be a non-empty string
    for topic in trends:
        assert isinstance(topic, str)
        assert topic

@pytest.mark.asyncio
async def test_fetch_google_trends(fetcher):
    """Test fetching Google Trends."""
    # Mock the PyTrends response
    mock_trends = ["Trend 1", "Trend 2", "Trend 3"]
    with patch.object(fetcher.pytrends, 'trending_searches', return_value=mock_trends):
        trends = await fetcher.fetch_trends("google", limit=2)
        assert isinstance(trends, list)
        assert len(trends) == 2
        assert trends == mock_trends[:2]

@pytest.mark.asyncio
async def test_fetch_google_trends_error(fetcher):
    """Test Google Trends error handling."""
    # Mock PyTrends to raise an exception
    with patch.object(fetcher.pytrends, 'trending_searches', side_effect=Exception("API Error")):
        trends = await fetcher.fetch_trends("google", limit=2)
        # Should fall back to mock data
        assert isinstance(trends, list)
        assert len(trends) == 2
        for topic in trends:
            assert isinstance(topic, str)
            assert topic

@pytest.mark.asyncio
async def test_invalid_source(fetcher):
    """Test handling of invalid source."""
    with pytest.raises(ValueError):
        await fetcher.fetch_trends("invalid_source", limit=3)

@pytest.mark.asyncio
async def test_youtube_api_error(fetcher):
    """Test handling of YouTube API errors."""
    # Patch the internal method to raise an exception and ensure it propagates as RuntimeError
    with patch.object(fetcher, '_fetch_youtube_trends', side_effect=Exception("API Error")):
        with pytest.raises(RuntimeError):
            await fetcher.fetch_trends("youtube", limit=3)