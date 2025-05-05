"""gRPC client for testing the TrendStory service."""

import asyncio
import grpc
import logging
from typing import Dict, Any, Optional

from trendstory.proto import trendstory_pb2
from trendstory.proto import trendstory_pb2_grpc
from .config import settings

logger = logging.getLogger(__name__)

class TrendStoryClient:
    """Client for the TrendStory gRPC service."""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """Initialize the client.
        
        Args:
            host: Server host (default from settings)
            port: Server port (default from settings)
        """
        self.host = host or settings.HOST
        self.port = port or settings.PORT
        self.channel = None
        self.stub = None
        
    async def connect(self):
        """Connect to the gRPC server."""
        self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
        self.stub = trendstory_pb2_grpc.TrendStoryStub(self.channel)
        
    async def close(self):
        """Close the connection."""
        if self.channel:
            await self.channel.close()
            
    async def generate_story(
        self, 
        source: str, 
        theme: str, 
        limit: int = 5
    ) -> Dict[str, Any]:
        """Generate a story from trending topics.
        
        Args:
            source: Source of trending topics (youtube, tiktok, google)
            theme: Theme for the story
            limit: Maximum number of topics to include
            
        Returns:
            Dictionary with story and metadata
            
        Raises:
            Exception: If there's an error generating the story
        """
        if not self.stub:
            await self.connect()
            
        request = trendstory_pb2.GenerateRequest(
            source=source,
            theme=theme,
            limit=limit
        )
        
        try:
            response = await self.stub.Generate(request)
            
            result = {
                "story": response.story,
                "status_code": response.status_code,
                "error_message": response.error_message,
                "topics_used": list(response.topics_used),
                "metadata": {
                    "generation_time": response.metadata.generation_time,
                    "model_name": response.metadata.model_name,
                    "source": response.metadata.source,
                    "theme": response.metadata.theme
                }
            }
            
            return result
            
        except grpc.RpcError as e:
            status_code = e.code()
            details = e.details()
            logger.error(f"RPC error: {status_code} - {details}")
            raise Exception(f"Error generating story: {details}")


async def main():
    """Test client main function."""
    client = TrendStoryClient()
    
    try:
        await client.connect()
        
        # Test with YouTube source and comedy theme
        print("Generating story with YouTube trends and comedy theme...")
        result = await client.generate_story("youtube", "comedy", 3)
        
        print("\nGenerated Story:")
        print("-" * 50)
        print(result["story"])
        print("-" * 50)
        print("\nTopics used:", result["topics_used"])
        print("Model:", result["metadata"]["model_name"])
        print("Generation time:", result["metadata"]["generation_time"])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())