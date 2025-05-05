import logging
from typing import List, Union, Dict
import os
from deepface import DeepFace
import cv2
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MoodRecognizer:
    """Class to recognize emotion (mood) from facial images using DeepFace."""

    def __init__(self):
        """Initialize the mood recognizer."""
        logger.info("MoodRecognizer initialized.")
        
        # Define emotion mappings with confidence thresholds
        self.emotion_map = {
            'angry': 'angry',
            'disgust': 'negative',
            'fear': 'anxious',
            'happy': 'happy',
            'sad': 'sad',
            'surprise': 'excited',
            'neutral': 'neutral'
        }
        
        # Confidence threshold for emotion detection
        self.confidence_threshold = 0.4

    def recognize_mood(self, image_path: Union[str, List[str]]) -> List[str]:
        """
        Analyze the given image(s) and return dominant emotions.

        Args:
            image_path (str or List[str]): Path(s) to image file(s).

        Returns:
            List[str]: Dominant emotions from each image.
        """
        if isinstance(image_path, str):
            image_path = [image_path]

        moods = []

        for path in image_path:
            try:
                # Verify image exists
                if not os.path.exists(path):
                    logger.error(f"Image file not found: {path}")
                    moods.append("neutral")
                    continue

                logger.info(f"Analyzing mood for image: {path}")
                
                # Use DeepFace with specific backend and model
                result = DeepFace.analyze(
                    img_path=path,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='retinaface'  # More accurate face detection
                )
                
                if result and isinstance(result, list) and len(result) > 0:
                    # Get emotion scores
                    emotions = result[0].get('emotion', {})
                    
                    if emotions:
                        # Log raw emotions for debugging
                        logger.info(f"Raw emotions detected: {emotions}")
                        
                        # Get the emotion with highest confidence
                        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                        emotion_name, confidence = dominant_emotion
                        
                        # Only use emotion if confidence is above threshold
                        if confidence > self.confidence_threshold:
                            mood = self.emotion_map.get(emotion_name, 'neutral')
                            logger.info(f"Detected emotion '{emotion_name}' with confidence {confidence:.2f} -> mapped to mood: {mood}")
                        else:
                            logger.warning(f"Emotion confidence {confidence:.2f} below threshold {self.confidence_threshold}")
                            mood = 'neutral'
                        
                        moods.append(mood)
                    else:
                        logger.warning("No emotions detected in analysis result")
                        moods.append("neutral")
                else:
                    logger.warning("Invalid analysis result format")
                    moods.append("neutral")
                    
            except Exception as e:
                logger.error(f"Failed to analyze image {path}: {e}")
                moods.append("neutral")

        return moods

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mood_recognizer.py <image_path1> [<image_path2> ...]")
    else:
        image_files = sys.argv[1:]
        recognizer = MoodRecognizer()
        results = recognizer.recognize_mood(image_files)

        for img, mood in zip(image_files, results):
            print(f"{img} → {mood}")

