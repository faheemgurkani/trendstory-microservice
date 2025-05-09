"""gRPC server for the TrendStory microservice."""

import logging
import time
import os
import sys
import asyncio
from concurrent import futures
import grpc
from trendstory.llm_engine import LLMEngine
from trendstory.trends_fetcher import TrendsFetcher
from trendstory.mood_recognizer import MoodRecognizer
from trendstory.proto import trendstory_pb2, trendstory_pb2_grpc
from trendstory.config import settings  # Import settings

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

class TrendStoryServicer(trendstory_pb2_grpc.TrendStoryServicer):
    """Implementation of TrendStory service."""
    
    def __init__(self):
        logger.info("Initializing TrendStoryServicer...")
        self.llm_engine = LLMEngine()
        self.trends_fetcher = TrendsFetcher()
        self.mood_recognizer = MoodRecognizer()
        logger.info("TrendStoryServicer initialized successfully")
    
    async def Generate(self, request, context):
        """Generate a story based on trending topics and theme."""
        try:
            logger.info(f"Received Generate request - Theme: {request.theme}, Source: {request.source}, Limit: {request.limit}")
            
            # Recognize mood from image if provided
            detected_mood = None
            if request.image_path and request.image_path.strip():
                image_path = request.image_path.strip()
                logger.info(f"Analyzing mood from image: {image_path}")
                
                # Verify image exists
                if not os.path.exists(image_path):
                    error_msg = f"Image file not found: {image_path}"
                    logger.error(error_msg)
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(error_msg)
                    return trendstory_pb2.GenerateResponse()
                
                try:
                    moods = self.mood_recognizer.recognize_mood(image_path)
                    if moods and moods[0] != "error":
                        detected_mood = moods[0]
                        logger.info(f"Detected mood: {detected_mood}")
                    else:
                        logger.warning("Failed to detect mood from image")
                except Exception as e:
                    logger.error(f"Error in mood recognition: {str(e)}")
                    detected_mood = "neutral"
            
            # Fetch trends (only once, regardless of source)
            logger.info("Fetching trends from news source")
            topics = await self.trends_fetcher.fetch_trends("news", limit=request.limit)
            logger.info(f"Fetched {len(topics)} topics")
            
            if not topics:
                error_msg = "Failed to fetch trending topics"
                logger.error(error_msg)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(error_msg)
                return trendstory_pb2.GenerateResponse()
            
            # Let LLM select theme based on mood if no theme provided
            selected_theme = request.theme
            if not selected_theme and detected_mood:
                try:
                    selected_theme = await self.llm_engine.select_theme_for_mood(detected_mood)
                    logger.info(f"LLM selected theme '{selected_theme}' based on mood '{detected_mood}'")
                except Exception as e:
                    logger.error(f"Error selecting theme for mood: {str(e)}")
                    selected_theme = "comedy"  # Default to comedy if theme selection fails
            elif not selected_theme:
                selected_theme = "comedy"  # Default theme if no mood and no theme provided

            # Ensure we have a valid theme
            if not selected_theme or selected_theme.strip() == "":
                selected_theme = "comedy"
                logger.warning("No theme selected, defaulting to 'comedy'")
            
            # Generate story
            logger.info(f"Generating story with theme: {selected_theme}")
            result = await self.llm_engine.generate_story(
                topics=topics,
                theme=selected_theme,  # Use the selected theme here
                mood=detected_mood
            )
            logger.info(f"Story generated successfully with theme: {selected_theme}")
            
            # Create metadata with guaranteed theme
            metadata = trendstory_pb2.StoryMetadata(
                generation_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                model_name=settings.MODEL_NAME,
                source=request.source,
                theme=selected_theme,  # Theme is guaranteed to have a value now
                mood=detected_mood or "neutral"
            )
            
            # Create response with all required fields
            response = trendstory_pb2.GenerateResponse(
                story=result["story"],
                status_code=0,
                error_message="",
                topics_used=topics,
                metadata=metadata,
                detected_mood=detected_mood or "neutral"
            )
            logger.info(f"Response prepared successfully with theme: {selected_theme}")
            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in Generate: {error_msg}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return trendstory_pb2.GenerateResponse(
                status_code=1,
                error_message=error_msg
            )

async def serve():
    """Start the gRPC server."""
    server = None
    try:
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        trendstory_pb2_grpc.add_TrendStoryServicer_to_server(
            TrendStoryServicer(), server
        )
        
        # Get host and port from environment variables
        host = os.getenv("TRENDSTORY_HOST", "0.0.0.0")
        port = int(os.getenv("TRENDSTORY_PORT", "50051"))
        
        server.add_insecure_port(f"{host}:{port}")
        logger.info(f"Starting gRPC server on {host}:{port}")
        
        await server.start()
        logger.info("Server started successfully")
        
        # Print a clear ready message
        print("\n" + "="*50)
        print("TrendStory gRPC Server is running!")
        print(f"Listening on {host}:{port}")
        print("Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        # Keep the server running
        try:
            await server.wait_for_termination()
        except asyncio.CancelledError:
            logger.info("Server shutdown initiated")
        finally:
            if server:
                await server.stop(0)
                logger.info("Server stopped gracefully")
            
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        if server:
            await server.stop(0)
        raise

def main():
    """Main entry point for the server."""
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the server
        loop.run_until_complete(serve())
    except KeyboardInterrupt:
        logger.info("Server shutdown complete")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up the event loop
        loop = asyncio.get_event_loop()
        loop.close()

if __name__ == "__main__":
    main() 