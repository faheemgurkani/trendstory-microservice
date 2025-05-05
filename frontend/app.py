import os
import time
import json
import grpc
import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tempfile
import base64
from io import BytesIO
import dotenv
import shutil

# Import proto-generated modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trendstory.proto import trendstory_pb2
from trendstory.proto import trendstory_pb2_grpc

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Backend connection settings
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "50051")

# Shared upload directory - use the absolute path to ensure backend can find it
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_UPLOAD_DIR = os.path.join(PROJECT_ROOT, "shared_uploads")

# Configuration
# SOURCES = ["youtube", "google", "all"]  # No longer needed
THEMES = [
    "comedy", "tragedy", "sarcasm", "mystery", "romance", 
    "adventure", "horror", "fantasy", "sci-fi", "inspirational"
]

# App title and configuration
st.set_page_config(
    page_title="TrendStory - AI Story Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "story" not in st.session_state:
    st.session_state.story = ""
if "topics" not in st.session_state:
    st.session_state.topics = []
if "image" not in st.session_state:
    st.session_state.image = None
if "detected_mood" not in st.session_state:
    st.session_state.detected_mood = None
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = None
if "image_path" not in st.session_state:
    st.session_state.image_path = None

# Create shared uploads directory if it doesn't exist
os.makedirs(SHARED_UPLOAD_DIR, exist_ok=True)

# Create gRPC channel and client
def get_grpc_client():
    # Set max message size limit
    options = [
        ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
        ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50MB
    ]
    channel = grpc.insecure_channel(f"{BACKEND_HOST}:{BACKEND_PORT}", options=options)
    return trendstory_pb2_grpc.TrendStoryStub(channel)

# Helper functions
def save_camera_image(image):
    """Save camera image to shared directory and return the path"""
    try:
        # Convert to PIL image
        pil_image = image
            
        # Generate filename with absolute path
        filename = f"camera_image_{int(time.time())}.jpg"
        filepath = os.path.join(SHARED_UPLOAD_DIR, filename)
        
        # Save image
        pil_image.save(filepath)
        
        # Return the absolute path
        return os.path.abspath(filepath)
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

def generate_story(source, theme, limit, image_path=None):
    """Generate a story by calling the backend gRPC API"""
    try:
        # Create gRPC client
        client = get_grpc_client()
        
        # Prepare request
        request = trendstory_pb2.GenerateRequest(
            source=source,
            theme=theme,
            limit=limit
        )
        
        # Add image path if available
        if image_path:
            request.image_path = image_path
        
        # Call the API
        response = client.Generate(request)
        
        # Check if request was successful
        if response.status_code == 0:
            result = {
                "story": response.story,
                "topics_used": list(response.topics_used),
                "detected_mood": response.detected_mood if response.detected_mood else None
            }
            
            # Get metadata
            if response.metadata:
                result["metadata"] = {
                    "theme": response.metadata.theme
                }
            
            return result
        else:
            st.error(f"Error generating story: {response.error_message}")
            return None
            
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

# App UI
st.title("📚 TrendStory Generator")
st.subheader("Create AI stories based on trending topics and your mood")

# Main app with tabs
tab1, tab2 = st.tabs(["Generate Story", "About"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    # Left Column - Controls and Image
    with col1:
        st.header("Settings")
        
        # Source selection removed; always use 'all'
        source = "all"
        
        # Camera capture for mood detection
        st.subheader("Take Photo for Mood Detection")
        camera_image = st.camera_input("Capture your photo")
        
        if camera_image is not None:
            # Display the captured image
            image = Image.open(camera_image)
            st.session_state.image = image
            
            # Save image immediately
            image_path = save_camera_image(image)
            if image_path:
                st.success("Image captured successfully!")
                st.session_state.image_path = image_path
                st.info("Your mood will be detected automatically when generating the story.")
        
        # Theme selection if not using mood
        use_mood = st.checkbox("Use mood detection", value=True, 
                              help="When enabled, a theme will be selected based on your facial expression")
        
        if not use_mood:
            # Let user select theme manually
            theme = st.selectbox("Select Theme", THEMES, index=0)
        else:
            theme = ""
            if st.session_state.selected_theme:
                st.info(f"Current detected theme: {st.session_state.selected_theme}")
        
        # Number of trends
        limit = 7  # Always use all available trends
        
        # Generate button
        if st.button("Generate Story", type="primary"):
            if use_mood and not st.session_state.image_path:
                st.error("Please take a photo first for mood detection.")
            else:
                with st.spinner("Generating your story..."):
                    # Generate story with or without mood detection
                    if use_mood:
                        result = generate_story(source, "", limit, st.session_state.image_path)
                    else:
                        result = generate_story(source, theme, limit)
                    
                    if result:
                        st.session_state.story = result.get("story", "")
                        st.session_state.topics = result.get("topics_used", [])
                        st.session_state.detected_mood = result.get("detected_mood")
                        
                        # Get theme from metadata
                        metadata = result.get("metadata", {})
                        if metadata:
                            st.session_state.selected_theme = metadata.get("theme")
        
        # Display topics if available
        if st.session_state.topics:
            st.subheader("Topics Used")
            for topic in st.session_state.topics:
                st.markdown(f"- {topic}")
    
    # Right Column - Story Output
    with col2:
        st.header("Generated Story")
        
        if st.session_state.story:
            # Display metadata
            if st.session_state.detected_mood:
                st.info(f"Detected Mood: {st.session_state.detected_mood}")
            
            if st.session_state.selected_theme:
                st.info(f"Theme: {st.session_state.selected_theme}")
            
            # Display the story
            st.markdown(st.session_state.story)
            
            # Download button
            st.download_button(
                "Download Story",
                st.session_state.story,
                file_name=f"trendstory_{source}_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.info("Your story will appear here. Take a photo and click 'Generate Story'.")

# About tab
with tab2:
    st.header("About TrendStory")
    
    st.markdown("""
    **TrendStory** is a microservice that generates themed stories based on trending topics 
    from YouTube and Google Trends. The system can detect your mood from a photo
    and generate stories that match your emotional state!
    
    ### Features:
    
    - **Trend-Based Stories**: Generate stories based on current trending topics
    - **Mood Detection**: Take a photo with your camera to determine your mood
    - **Background Removal**: Uses AI to remove image backgrounds for better mood detection
    - **Theme Selection**: Automatically selects appropriate themes based on your mood
    - **Multiple Sources**: Get trends from YouTube, Google, or both
    
    ### How It Works:
    
    1. Take a photo with your camera
    2. Background removal is applied for better face detection
    3. DeepFace analyzes your facial expression to determine your mood
    4. An appropriate theme is selected based on your mood
    5. Trending topics are fetched from your selected source
    6. A large language model generates a story combining the theme and trending topics
    
    Built with ❤️ using gRPC, Python, Streamlit, and AI.
    """)

# Footer
st.divider()
st.caption("TrendStory Microservice © 2025") 