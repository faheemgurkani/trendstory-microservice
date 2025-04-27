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

class TrendStoryServicer(trendstory_pb2_grpc.TrendStoryServicer):
    """Implementation of TrendStory service."""
    
    def __init__(self):
        logger.info("Initializing TrendStoryServicer...")
        self.llm_engine = LLMEngine()
        self.trends_fetcher = TrendsFetcher()
        logger.info("TrendStoryServicer initialized successfully")
    
    async def Generate(self, request, context):
        """Generate a story based on trending topics and theme."""
        try:
            logger.info(f"Received Generate request - Theme: {request.theme}, Source: {request.source}, Limit: {request.limit}")
            
            # Fetch trends based on source
            logger.info(f"Fetching trends from source: {request.source}")
            youtube_trends = []
            google_trends = []
            
            if request.source in ["youtube", "all"]:
                youtube_trends = await self.trends_fetcher.fetch_trends("youtube", limit=request.limit)
                logger.info(f"Fetched {len(youtube_trends)} YouTube trends")
            
            if request.source in ["google", "all"]:
                google_trends = await self.trends_fetcher.fetch_trends("google", limit=request.limit)
                logger.info(f"Fetched {len(google_trends)} Google trends")
            
            topics = youtube_trends + google_trends
            logger.info(f"Total topics fetched: {len(topics)}")
            
            if not topics:
                error_msg = "Failed to fetch trending topics from any source"
                logger.error(error_msg)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(error_msg)
                return trendstory_pb2.GenerateResponse()
            
            # Generate story
            logger.info(f"Generating story with theme: {request.theme}")
            result = await self.llm_engine.generate_story(
                topics=topics,
                theme=request.theme
            )
            logger.info("Story generated successfully")
            
            # Create metadata
            metadata = trendstory_pb2.StoryMetadata(
                generation_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                model_name=os.getenv("TRENDSTORY_MODEL_NAME", "t5-small"),
                source=request.source,
                theme=request.theme
            )
            
            response = trendstory_pb2.GenerateResponse(
                story=result["story"],
                status_code=0,
                error_message="",
                topics_used=topics,
                metadata=metadata
            )
            logger.info("Response prepared successfully")
            return response
            
        except Exception as e:
            error_msg = f"Error generating story: {str(e)}"
            logger.error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return trendstory_pb2.GenerateResponse()

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