"""gRPC client for the TrendStory microservice."""

import asyncio
import logging
import os
import sys
import grpc
from trendstory.proto import trendstory_pb2, trendstory_pb2_grpc
from trendstory.config import settings  # Import settings
from trendstory.camera_capture import CameraCapture  # Import camera capture

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
    
    async def generate_story(self, theme, source="all", limit=5, image_path=None):
        """Generate a story with the given theme and source."""
        try:
            logger.info(f"Sending request - Theme: {theme}, Source: {source}, Limit: {limit}")
            if image_path:
                # Convert to absolute path
                abs_image_path = os.path.abspath(image_path)
                logger.info(f"Including image for mood recognition: {abs_image_path}")
            
            request = trendstory_pb2.GenerateRequest(
                theme=theme,
                source=source,
                limit=limit,
                image_path=abs_image_path if image_path else ""
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
                "detected_mood": response.detected_mood,
                "metadata": {
                    "generation_time": response.metadata.generation_time,
                    "model_name": response.metadata.model_name,
                    "source": response.metadata.source,
                    "theme": response.metadata.theme,
                    "mood": response.metadata.mood
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
    
    # Use settings from config
    client = TrendStoryClient(
        host=settings.HOST,
        port=settings.PORT
    )
    
    try:
        # Capture photo from camera
        logger.info("Initializing camera for mood capture...")
        camera = CameraCapture()
        try:
            logger.info("Taking photo with background removal...")
            image_path = camera.capture_photo(remove_bg=True)
            logger.info(f"Photo captured and background removed: {image_path}")
        except RuntimeError as e:
            logger.error(f"Failed to capture photo: {e}")
            return
        
        # Generate a story
        logger.info("Requesting story generation")
        result = await client.generate_story(
            theme=None,  # Let the LLM choose theme based on mood
            source="all",
            limit=3,
            image_path=image_path  # Use the captured image
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
            
            # Get theme from metadata, defaulting to 'comedy' if not present
            theme = result["metadata"].get("theme", "comedy")
            
            print("\n" + "="*50)
            print("Story Theme Selection:")
            print("="*50)
            print(f"1. Detected Mood from Photo: {result['detected_mood']}")
            print(f"2. Selected Theme Based on Mood: {theme}")  # Use the theme we extracted
            print(f"3. Story Generated Using Theme: {theme}")  # Use the same theme
            
            print("\n" + "="*50)
            print("Generation Details:")
            print("="*50)
            print(f"Time: {result['metadata']['generation_time']}")
            print(f"Model: {result['metadata']['model_name']}")
            print(f"Source: {result['metadata']['source']}")
            print()
            
            logger.info(f"Photo saved in CAMERAPIC folder: {image_path}")
            logger.info(f"Story generated with theme: {theme}")  # Log the theme
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