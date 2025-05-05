"""Unit tests for the TrendStory service."""

import unittest
import asyncio
import grpc
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from trendstory.service import TrendStoryServicer
from trendstory.proto import trendstory_pb2

class TestTrendStoryService(unittest.TestCase):
    """Test cases for TrendStory service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.servicer = TrendStoryServicer()
        self.servicer.trends_fetcher = AsyncMock()
        self.servicer.llm_engine = AsyncMock()
        self.context = AsyncMock()
        
        # Sample mock data
        self.mock_topics = ["Topic 1", "Topic 2", "Topic 3"]
        self.mock_story_result = {
            "story": "This is a test story about Topic 1 and Topic 2.",
            "metadata": {
                "generation_time": "2025-04-22T12:00:00",
                "model_name": "test-model",
                "theme": "comedy",
                "topics_used": self.mock_topics
            }
        }
        
        # Set up mock response
        self.servicer.trends_fetcher.fetch_trends.return_value = self.mock_topics
        self.servicer.llm_engine.generate_story.return_value = self.mock_story_result
        
    @pytest.mark.asyncio
    async def test_generate_valid_request(self):
        """Test Generate with valid request."""
        # Create request
        request = trendstory_pb2.GenerateRequest(
            source="youtube",
            theme="comedy",
            limit=3
        )
        
        # Call the service method
        response = await self.servicer.Generate(request, self.context)
        
        # Verify trends fetcher was called correctly
        self.servicer.trends_fetcher.fetch_trends.assert_called_once_with("youtube", 3)
        
        # Verify LLM engine was called correctly
        self.servicer.llm_engine.generate_story.assert_called_once_with(
            self.mock_topics, "comedy"
        )
        
        # Verify response fields
        self.assertEqual(response.story, self.mock_story_result["story"])
        self.assertEqual(response.status_code, 0)
        self.assertEqual(response.error_message, "")
        self.assertEqual(list(response.topics_used), self.mock_topics)
        self.assertEqual(response.metadata.model_name, "test-model")
        self.assertEqual(response.metadata.theme, "comedy")
        
    @pytest.mark.asyncio
    async def test_generate_invalid_source(self):
        """Test Generate with invalid source."""
        # Create request with invalid source
        request = trendstory_pb2.GenerateRequest(
            source="invalid_source",
            theme="comedy",
            limit=3
        )
        
        # Set up context to track aborts
        self.context.abort = AsyncMock()
        
        # Call the service method
        await self.servicer.Generate(request, self.context)
        
        # Verify context.abort was called with INVALID_ARGUMENT
        self.context.abort.assert_called_once()
        args = self.context.abort.call_args[0]
        self.assertEqual(args[0], grpc.StatusCode.INVALID_ARGUMENT)
        
    @pytest.mark.asyncio
    async def test_generate_trends_fetcher_error(self):
        """Test Generate when trends fetcher raises an error."""
        # Create request
        request = trendstory_pb2.GenerateRequest(
            source="youtube",
            theme="comedy",
            limit=3
        )
        
        # Set trends fetcher to raise exception
        self.servicer.trends_fetcher.fetch_trends.side_effect = RuntimeError("API error")
        
        # Set up context to track aborts
        self.context.abort = AsyncMock()
        
        # Call the service method
        await self.servicer.Generate(request, self.context)
        
        # Verify context.abort was called with INTERNAL
        self.context.abort.assert_called_once()
        args = self.context.abort.call_args[0]
        self.assertEqual(args[0], grpc.StatusCode.INTERNAL)
        
    @pytest.mark.asyncio
    async def test_generate_llm_engine_error(self):
        """Test Generate when LLM engine raises an error."""
        # Create request
        request = trendstory_pb2.GenerateRequest(
            source="youtube",
            theme="comedy",
            limit=3
        )
        
        # Set LLM engine to raise exception
        self.servicer.llm_engine.generate_story.side_effect = RuntimeError("Model error")
        
        # Set up context to track aborts
        self.context.abort = AsyncMock()
        
        # Call the service method
        await self.servicer.Generate(request, self.context)
        
        # Verify context.abort was called with INTERNAL
        self.context.abort.assert_called_once()
        args = self.context.abort.call_args[0]
        self.assertEqual(args[0], grpc.StatusCode.INTERNAL)
        
    @pytest.mark.asyncio
    async def test_generate_default_limit(self):
        """Test Generate with default limit."""
        # Create request without limit
        request = trendstory_pb2.GenerateRequest(
            source="youtube",
            theme="comedy"
        )
        
        # Call the service method
        await self.servicer.Generate(request, self.context)
        
        # Verify trends fetcher was called with default limit (5)
        self.servicer.trends_fetcher.fetch_trends.assert_called_once()
        args = self.servicer.trends_fetcher.fetch_trends.call_args[0]
        self.assertEqual(args[1], 5)  # Default limit should be 5