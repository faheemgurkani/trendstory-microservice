#!/usr/bin/env python
"""
Test script for camera capture with background removal.
This is a standalone script that doesn't depend on the gRPC server/client.
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Import the camera capture directly
from trendstory.camera_capture import CameraCapture

def main():
    """
    Capture a photo with background removal and print the path.
    """
    try:
        logger.info("Initializing camera for test...")
        camera = CameraCapture()
        
        logger.info("Taking photo with background removal...")
        image_path = camera.capture_photo(remove_bg=True)
        
        logger.info(f"Test successful! Photo saved to: {image_path}")
        logger.info("Background has been removed from the image.")
        
        print("\n" + "="*50)
        print(f"Image saved to: {image_path}")
        print("="*50 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 