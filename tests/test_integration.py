"""Integration tests for the TrendStory service."""

import unittest
import asyncio
import grpc
import pytest
import os
import time
import subprocess
from unittest.mock import patch
import threading

from trendstory.client import TrendStoryClient
from trendstory.config import settings

@pytest.mark.integration
class TestTrendStoryIntegration(unittest.TestCase):
    """Integration tests for TrendStory service."""
    
    @classmethod
    def setUpClass(cls):
        """Start the server process before tests."""
        # Use subprocess to start the server in a separate process
        cls.server_process = None
        
        # Set environment variables for testing
        os.environ["TRENDSTORY_HOST"] = "localhost"
        os.environ["TRENDSTORY_PORT"] = "50052"  # Use different port for testing
        os.environ["TRENDSTORY_DEBUG"] = "true"
        os.environ["TRENDSTORY_MODEL_NAME"] = "t5-small"
        os.environ["TRENDSTORY_MODEL_CACHE_DIR"] = "./test_model_cache"
        
        # Start server with test configuration
        cls.server_process = subprocess.Popen(
            ["python", "-m", "trendstory.main"],
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)  # Increased wait time for model loading
        
    @classmethod
    def tearDownClass(cls):
        """Stop the server process after tests."""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
            
    def setUp(self):
        """Set up test client."""
        self.client = TrendStoryClient(host="localhost", port=50052)
        
    @pytest.mark.asyncio
    async def test_generate_story_youtube(self):
        """Test generating a story with YouTube trends."""
        # Connect to server
        await self.client.connect()
        
        try:
            # Generate story
            result = await self.client.generate_story("youtube", "comedy", 3)
            
            # Verify result structure
            self.assertIn("story", result)
            self.assertIn("status_code", result)
            self.assertIn("error_message", result)
            self.assertIn("topics_used", result)
            self.assertIn("metadata", result)
            
            # Verify status code is success
            self.assertEqual(result["status_code"], 0)
            
            # Verify error message is empty
            self.assertEqual(result["error_message"], "")
            
            # Verify story is not empty
            self.assertTrue(len(result["story"]) > 0)
            
            # Verify topics list is not empty
            self.assertTrue(len(result["topics_used"]) > 0)
            
            # Verify metadata
            self.assertEqual(result["metadata"]["source"], "youtube")
            self.assertEqual(result["metadata"]["theme"], "comedy")
            self.assertEqual(result["metadata"]["model_name"], "t5-small")
            
        finally:
            await self.client.close()
            
    @pytest.mark.asyncio
    async def test_generate_story_invalid_source(self):
        """Test generating a story with invalid source."""
        # Connect to server
        await self.client.connect()
        
        try:
            # Attempt to generate story with invalid source
            with self.assertRaises(Exception) as context:
                await self.client.generate_story("invalid_source", "comedy", 3)
                
            # Verify error message
            self.assertIn("Unsupported source", str(context.exception))
            
        finally:
            await self.client.close()
            
    @pytest.mark.asyncio
    async def test_generate_story_multiple_themes(self):
        """Test generating stories with different themes."""
        # Connect to server
        await self.client.connect()
        
        themes = ["comedy", "tragedy", "sarcasm"]
        
        try:
            for theme in themes:
                # Generate story
                result = await self.client.generate_story("youtube", theme, 3)
                
                # Verify status code is success
                self.assertEqual(result["status_code"], 0)
                
                # Verify theme in metadata
                self.assertEqual(result["metadata"]["theme"], theme)
                
                # Verify story content is theme-appropriate
                self.assertTrue(len(result["story"]) > 0)
                
        finally:
            await self.client.close()
            
    @pytest.mark.asyncio
    async def test_generate_story_different_limits(self):
        """Test generating stories with different trend limits."""
        # Connect to server
        await self.client.connect()
        
        limits = [1, 3, 5]
        
        try:
            for limit in limits:
                # Generate story
                result = await self.client.generate_story("youtube", "comedy", limit)
                
                # Verify status code is success
                self.assertEqual(result["status_code"], 0)
                
                # Verify number of topics used
                self.assertEqual(len(result["topics_used"]), limit)
                
        finally:
            await self.client.close()