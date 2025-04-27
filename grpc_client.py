"""gRPC client for the TrendStory microservice."""

import asyncio
import logging
import os
import sys
import grpc
from proto import trendstory_pb2, trendstory_pb2_grpc

# Configure logging
class SpacedFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        return f"\n{message}\n"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(SpacedFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

class TrendStoryClient:
    """Client for interacting with the TrendStory gRPC service."""
    
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("TRENDSTORY_HOST", "localhost")
        self.port = port or int(os.getenv("TRENDSTORY_PORT", "50051"))
        logger.info(f"Initializing client to connect to {self.host}:{self.port}")
        
        try:
            self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self.stub = trendstory_pb2_grpc.TrendStoryStub(self.channel)
            logger.info("Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize client: {str(e)}")
            raise
    
    async def generate_story(self, theme, source="all", limit=5):
        """Generate a story with the given theme and source."""
        try:
            logger.info(f"Sending request - Theme: {theme}, Source: {source}, Limit: {limit}")
            
            request = trendstory_pb2.GenerateRequest(
                theme=theme,
                source=source,
                limit=limit
            )
            
            logger.info("Waiting for server response...")
            response = await self.stub.Generate(request)
            logger.info("Received response from server")
            
            if response.status_code != 0:
                error_msg = f"Server returned error: {response.error_message}"
                logger.error(error_msg)
                return None
            
            result = {
                "story": response.story,
                "topics_used": response.topics_used,
                "metadata": {
                    "generation_time": response.metadata.generation_time,
                    "model_name": response.metadata.model_name,
                    "source": response.metadata.source,
                    "theme": response.metadata.theme
                }
            }
            
            logger.info("Successfully processed response")
            return result
            
        except grpc.RpcError as e:
            logger.error(f"RPC failed: {e.code()}: {e.details()}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    async def close(self):
        """Close the gRPC channel."""
        try:
            await self.channel.close()
            logger.info("Client channel closed successfully")
        except Exception as e:
            logger.error(f"Error closing channel: {str(e)}")

async def main():
    """Example usage of the TrendStory client."""
    logger.info("Starting client example")
    client = TrendStoryClient()
    
    try:
        # Generate a story
        logger.info("Requesting story generation")
        result = await client.generate_story(
            theme="comedy",
            source="all",
            limit=3
        )
        
        if result:
            print("\n" + "="*50)
            print("Generated Story:")
            print("="*50)
            print(result["story"])
            
            print("\n" + "="*50)
            print("Topics Used:")
            print("="*50)
            for topic in result["topics_used"]:
                print(f"- {topic}")
            
            print("\n" + "="*50)
            print("Metadata:")
            print("="*50)
            for key, value in result["metadata"].items():
                print(f"{key}: {value}")
            # print("="*50 + "\n")
        else:
            logger.error("Failed to generate story")
    
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        await client.close()
        logger.info("Client example completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1) 