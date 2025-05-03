import logging
from typing import List, Union

from deepface import DeepFace

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



class MoodRecognizer:
    """Class to recognize emotion (mood) from facial images using DeepFace."""

    def __init__(self):
        """Initialize the mood recognizer."""
        logger.info("MoodRecognizer initialized.")

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
                logger.info(f"Analyzing mood for image: {path}")
                result = DeepFace.analyze(img_path=path, actions=['emotion'])
                mood = result[0]["dominant_emotion"]
                moods.append(mood)
                logger.info(f"Detected emotion: {mood}")
            except Exception as e:
                logger.error(f"Failed to analyze image {path}: {e}")
                moods.append("error")

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

