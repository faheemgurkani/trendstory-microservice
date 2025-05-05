"""Module for real-time camera capture and image saving."""

import cv2
import os
import logging
from datetime import datetime
import numpy as np
from rembg import remove
from PIL import Image
import io

logger = logging.getLogger(__name__)

class CameraCapture:
    """Class to handle real-time camera capture."""
    
    def __init__(self):
        """Initialize the camera capture."""
        self.camera = None
        # Create CAMERAPIC directory in the current working directory
        self.pics_dir = os.path.join(os.getcwd(), "CAMERAPIC")
        os.makedirs(self.pics_dir, exist_ok=True)
        
    def remove_background(self, image_path):
        """
        Remove background from an image.
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            str: Path to the background-removed image
        """
        try:
            # Generate output filename
            filename, ext = os.path.splitext(image_path)
            output_path = f"{filename}_nobg{ext}"
            
            # Open image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                
            # Remove background
            output_data = remove(img_data)
            
            # Save output image
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
                
            logger.info(f"Background removed, saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to remove background: {str(e)}")
            return image_path  # Return original image if processing fails
        
    def capture_photo(self, remove_bg=True) -> str:
        """
        Open camera, capture a photo, and save it.
        
        Args:
            remove_bg (bool): Whether to remove background from the captured image
            
        Returns:
            str: Path to the saved image file
        
        Raises:
            RuntimeError: If camera cannot be accessed or image cannot be saved
        """
        try:
            # Initialize camera (0 is usually the default webcam)
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                raise RuntimeError("Could not access camera")
            
            logger.info("Camera initialized successfully")
            
            # Create a window to display the camera feed
            cv2.namedWindow("Camera Feed - Press SPACE to capture, ESC to cancel", cv2.WINDOW_NORMAL)
            
            while True:
                # Read frame from camera
                ret, frame = self.camera.read()
                if not ret:
                    raise RuntimeError("Failed to capture frame from camera")
                
                # Display the frame
                cv2.imshow("Camera Feed - Press SPACE to capture, ESC to cancel", frame)
                
                # Wait for key press
                key = cv2.waitKey(1) & 0xFF
                
                # If SPACE is pressed, save the image
                if key == 32:  # SPACE key
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(self.pics_dir, f"mood_capture_{timestamp}.jpg")
                    
                    # Save the image
                    cv2.imwrite(image_path, frame)
                    logger.info(f"Photo captured and saved to: {image_path}")
                    
                    # Remove background if requested
                    if remove_bg:
                        logger.info("Removing background from captured image...")
                        image_path = self.remove_background(image_path)
                    
                    break
                
                # If ESC is pressed, cancel
                elif key == 27:  # ESC key
                    raise RuntimeError("Photo capture cancelled by user")
            
            return image_path
            
        except Exception as e:
            raise RuntimeError(f"Error during camera capture: {str(e)}")
        
        finally:
            # Clean up
            if self.camera is not None:
                self.camera.release()
            cv2.destroyAllWindows()
            
    def __del__(self):
        """Ensure camera is released when object is destroyed."""
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the camera capture
    try:
        capture = CameraCapture()
        image_path = capture.capture_photo(remove_bg=True)
        print(f"Test capture successful. Image saved to: {image_path}")
    except Exception as e:
        print(f"Test capture failed: {str(e)}") 