"""Entry point for the TrendStory gRPC server."""

import os
import sys
import logging
import asyncio
import grpc
import signal
from concurrent import futures

from .service import TrendStoryServicer
from .config import settings
from trendstory.proto import trendstory_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def serve():
    """Start the gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ]
    )
    
    # Add servicer to server
    trendstory_servicer = TrendStoryServicer()
    trendstory_pb2_grpc.add_TrendStoryServicer_to_server(
        trendstory_servicer, server
    )
    
    # Add port
    server_address = f"{settings.HOST}:{settings.PORT}"
    server.add_insecure_port(server_address)
    
    # Start server
    await server.start()
    logger.info(f"Server started on {server_address}")
    
    # Handle shutdown gracefully
    async def shutdown():
        logger.info("Shutting down server...")
        await server.stop(5)  # 5 seconds grace period
        
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
        
    # Keep server running until interrupted
    try:
        await server.wait_for_termination()
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        await shutdown()
        

def run_server():
    """Run the server."""
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()