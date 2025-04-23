import os
import sys
import json
import grpc
import streamlit as st
from typing import Dict, List, Any, Optional
import requests
from pathlib import Path

# Add the parent directory to sys.path to import the trendstory package
sys.path.append(str(Path(__file__).parent.parent))

# Import the generated gRPC modules
try:
    from proto import trendstory_pb2, trendstory_pb2_grpc
except ImportError:
    st.error("Failed to import proto modules. Make sure you've compiled the proto files.")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="TrendStory Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
SOURCES = ["youtube", "tiktok", "google"]
THEMES = [
    "comedy", "tragedy", "sarcasm", "mystery", "romance", 
    "adventure", "horror", "fantasy", "sci-fi", "inspirational"
]
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "50051"

# Use the session state to store the generated story
if "story" not in st.session_state:
    st.session_state.story = ""
if "trends" not in st.session_state:
    st.session_state.trends = []


def fetch_trending_topics(source: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch trending topics for preview in the UI.
    In a production app, this would call the actual API, but for simplicity
    we're using a mock implementation here.
    """
    # Mock data for demonstration purposes
    mock_data = {
        "youtube": [
            {"title": "New iPhone Launch Event", "views": "2.3M"},
            {"title": "World Cup Final Highlights", "views": "5.1M"},
            {"title": "SpaceX Starship Test Flight", "views": "3.7M"},
            {"title": "Celebrity Wedding Drama", "views": "1.8M"},
            {"title": "Viral Dance Challenge", "views": "4.2M"},
        ],
        "tiktok": [
            {"title": "#DanceChallenge2025", "views": "15.3M"},
            {"title": "#CookingHacks", "views": "8.7M"},
            {"title": "#PetTricks", "views": "12.5M"},
            {"title": "#LifeHack", "views": "10.1M"},
            {"title": "#FitnessJourney", "views": "9.4M"},
        ],
        "google": [
            {"title": "Local Elections", "trends": "1.5M searches"},
            {"title": "New Vaccine Development", "trends": "1.2M searches"},
            {"title": "Stock Market Crash", "trends": "2.1M searches"},
            {"title": "New Movie Release", "trends": "0.8M searches"},
            {"title": "Natural Disaster Updates", "trends": "1.7M searches"},
        ],
    }
    
    return mock_data.get(source, [])[:limit]


def generate_story(source: str, theme: str, limit: int) -> str:
    """
    Call the gRPC service to generate a story based on trending topics.
    """
    host = os.environ.get("TRENDSTORY_HOST", DEFAULT_HOST)
    port = os.environ.get("TRENDSTORY_PORT", DEFAULT_PORT)
    
    try:
        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = trendstory_pb2_grpc.TrendStoryStub(channel)
        
        request = trendstory_pb2.GenerateRequest(
            source=source,
            theme=theme,
            limit=limit,
        )
        
        response = stub.Generate(request)
        return response.story
    except grpc.RpcError as e:
        st.error(f"RPC Error: {e.details()}")
        return f"Error: {e.details()}"
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return f"Error: {str(e)}"


def on_generate_click():
    """Callback for the generate button"""
    source = st.session_state.source
    theme = st.session_state.theme
    limit = st.session_state.limit
    
    with st.spinner("Generating your story, please wait..."):
        # First, fetch trends for preview
        st.session_state.trends = fetch_trending_topics(source, limit)
        
        # Then generate the story
        st.session_state.story = generate_story(source, theme, limit)


# UI Layout
st.title("📚 TrendStory Generator")
st.subheader("Create themed stories based on trending topics")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Form for story generation parameters
    st.subheader("Story Parameters")
    source = st.selectbox("Source", options=SOURCES, key="source")
    theme = st.selectbox("Theme", options=THEMES, key="theme")
    limit = st.slider("Number of Trends", min_value=1, max_value=10, value=5, key="limit")
    
    # Generate button
    st.button("Generate Story", on_click=on_generate_click, type="primary")
    
    # Advanced settings (could be expanded in the future)
    with st.expander("Advanced Settings"):
        st.text_input("gRPC Host", value=DEFAULT_HOST, key="host")
        st.text_input("gRPC Port", value=DEFAULT_PORT, key="port")
    
    # About section
    st.divider()
    st.subheader("About")
    st.write("""
    TrendStory is a microservice that generates themed stories based on trending topics 
    from YouTube, TikTok, and Google Trends.
    """)
    st.write("Built with ❤️ using gRPC, Python, and LLMs.")

# Main area
col1, col2 = st.columns([1, 2])

# Left column for trends
with col1:
    st.subheader("Trending Topics")
    if st.session_state.trends:
        for i, trend in enumerate(st.session_state.trends, 1):
            with st.container():
                st.write(f"**{i}. {trend['title']}**")
                metrics = list(trend.items())[1]  # Get the second key-value pair (e.g., views or trends)
                st.caption(f"{metrics[0].title()}: {metrics[1]}")
                st.divider()
    else:
        st.info("Click 'Generate Story' to fetch trending topics.")

# Right column for the story
with col2:
    st.subheader("Generated Story")
    if st.session_state.story:
        st.write(st.session_state.story)
        
        # Add some action buttons
        col_download, col_copy, col_clear = st.columns(3)
        with col_download:
            st.download_button(
                "Download Story",
                data=st.session_state.story,
                file_name=f"trendstory_{st.session_state.source}_{st.session_state.theme}.txt",
                mime="text/plain",
            )
        with col_copy:
            # In a real app, you'd use JavaScript for clipboard functionality
            st.button("Copy to Clipboard", disabled=True, help="Not available in this version")
        with col_clear:
            if st.button("Clear Story"):
                st.session_state.story = ""
                st.session_state.trends = []
                st.experimental_rerun()
    else:
        st.info("Your generated story will appear here.")
        
# Footer
st.divider()
st.caption("TrendStory Microservice © 2025")