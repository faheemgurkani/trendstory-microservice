"""FastAPI server for the TrendStory microservice."""

import logging
import time
import psutil
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from trendstory.llm_engine import LLMEngine
from trendstory.trends_fetcher import TrendsFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TrendStory API",
    description="API for generating themed stories from trending topics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_engine = LLMEngine()
trends_fetcher = TrendsFetcher()

# Performance monitoring middleware
@app.middleware("http")
async def performance_monitoring(request: Request, call_next):
    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    response = await call_next(request)
    
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    response_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Response time: {response_time:.2f} seconds")
    logger.info(f"Memory used: {memory_used:.2f} MB")
    
    return response

class StoryRequest(BaseModel):
    """Request model for story generation."""
    theme: str = Field(
        ...,
        description="Theme for the story (e.g., comedy, tragedy, mystery)",
        example="comedy"
    )
    topics: Optional[List[str]] = Field(
        None,
        description="Optional list of topics to use. If not provided, will fetch trending topics."
    )
    source: Optional[str] = Field(
        "all",
        description="Source for trending topics ('youtube', 'google', or 'all')",
        example="all"
    )

class StoryResponse(BaseModel):
    """Response model for generated story."""
    story: str = Field(..., description="The generated story")
    metadata: dict = Field(..., description="Metadata about the generation process")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "TrendStory API",
        "version": "1.0.0",
        "description": "API for generating themed stories from trending topics"
    }

@app.post("/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """Generate a story based on trending topics and theme."""
    try:
        # If topics not provided, fetch them
        if not request.topics:
            logger.info(f"\nFetching trends from source: {request.source}\n")
            youtube_trends = []
            google_trends = []
            
            if request.source in ["youtube", "all"]:
                youtube_trends = await trends_fetcher.fetch_trends("youtube", limit=3)
            
            if request.source in ["google", "all"]:
                google_trends = await trends_fetcher.fetch_trends("google", limit=3)
            
            request.topics = youtube_trends + google_trends
            
            if not request.topics:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch trending topics from any source"
                )
        
        # Generate story
        logger.info(f"\nGenerating story with theme: {request.theme}\n")
        result = await llm_engine.generate_story(
            topics=request.topics,
            theme=request.theme
        )
        
        return StoryResponse(
            story=result["story"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"\nError generating story: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating story: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 