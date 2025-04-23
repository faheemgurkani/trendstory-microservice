"""Implementation of the TrendStory gRPC service."""

import logging
import asyncio
import grpc
from datetime import datetime, timezone
from typing import List, Dict, Any

from .trends_fetcher import TrendsFetcher
from .llm_engine import LLMEngine
from .config import settings

# Import generated gRPC code
from proto import trendstory_pb2
from proto import trendstory_pb2_grpc

logger = logging.getLogger(__name__)

class TrendStoryServicer(trendstory_pb2_grpc.TrendStoryServicer):
    """Implements the TrendStory gRPC service."""
    
    def __init__(self):
        """Initialize the servicer with required components."""
        self.trends_fetcher = TrendsFetcher()
        self.llm_engine = LLMEngine()
        
    async def Generate(
        self, 
        request: trendstory_pb2.GenerateRequest, 
        context: grpc.aio.ServicerContext
    ) -> trendstory_pb2.GenerateResponse:
        """Generate a themed story based on trending topics.
        
        Args:
            request: The request containing source, theme, and limit
            context: The gRPC context
            
        Returns:
            Response containing the generated story
        """
        try:
            logger.info(f"Received Generate request: source={request.source}, theme={request.theme}, limit={request.limit}")
            
            # Validate request
            if not request.source:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Source must be specified")
                
            if request.source not in settings.SUPPORTED_SOURCES:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, 
                    f"Unsupported source: {request.source}. Supported sources: {settings.SUPPORTED_SOURCES}"
                )
                
            if request.theme and request.theme not in settings.SUPPORTED_THEMES:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    f"Unsupported theme: {request.theme}. Supported themes: {settings.SUPPORTED_THEMES}"
                )
            
            # Use defaults if not specified
            theme = request.theme if request.theme else "default"
            limit = request.limit if request.limit > 0 else settings.DEFAULT_TRENDS_LIMIT
            
            # Fetch trending topics
            try:
                topics = await self.trends_fetcher.fetch_trends(request.source, limit)
            except ValueError as e:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
                return trendstory_pb2.GenerateResponse()  # Never reached due to abort
            except RuntimeError as e:
                await context.abort(grpc.StatusCode.INTERNAL, str(e))
                return trendstory_pb2.GenerateResponse()  # Never reached due to abort
                
            logger.info(f"Fetched {len(topics)} topics from {request.source}")
            
            # Generate story using LLM
            try:
                result = await self.llm_engine.generate_story(topics, theme)
            except RuntimeError as e:
                await context.abort(grpc.StatusCode.INTERNAL, str(e))
                return trendstory_pb2.GenerateResponse()  # Never reached due to abort
                
            # Create response with metadata
            metadata = trendstory_pb2.StoryMetadata(
                generation_time=result["metadata"]["generation_time"],
                model_name=result["metadata"]["model_name"],
                source=request.source,
                theme=theme
            )
            
            response = trendstory_pb2.GenerateResponse(
                story=result["story"],
                status_code=0,  # 0 = success
                error_message="",
                topics_used=topics,
                metadata=metadata
            )
            
            logger.info(f"Successfully generated story with {len(topics)} topics")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error in Generate: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal server error: {str(e)}")
            return trendstory_pb2.GenerateResponse()  # Never reached due to abort