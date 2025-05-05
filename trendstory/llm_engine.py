"""Module for using Dolphin LLM via Ollama API to generate stories."""

import os
import logging
import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .config import settings

logger = logging.getLogger(__name__)

class LLMEngine:
    """Engine for text generation using Dolphin LLM via Ollama."""
    
    def __init__(self):
        """Initialize the LLM engine."""
        self.model_name = settings.MODEL_NAME
        self.api_url = settings.OLLAMA_API_URL
        self.is_initialized = False
        self.session = None
        
        # Log start of initialization
        logger.info(f"\n\nStarting async initialization for model {self.model_name}...\n")
        
        # Start initialization asynchronously
        self.init_task = asyncio.create_task(self.initialize())
        
    async def initialize(self):
        """Initialize the aiohttp session and test Ollama connection."""
        if self.is_initialized:
            return
            
        try:
            # Create aiohttp session
            self.session = aiohttp.ClientSession()
            
            # Test connection to Ollama
            async with self.session.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": "test",
                    "stream": False
                }
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to connect to Ollama API: {response.status}")
                
            self.is_initialized = True
            logger.info(f"\n\nSuccessfully connected to Ollama API for model {self.model_name}\n")
            
        except Exception as e:
            logger.error(f"\nError initializing Ollama connection: {str(e)}\n")
            if self.session:
                await self.session.close()
            raise RuntimeError(f"Failed to initialize Ollama connection: {str(e)}")
    
    async def select_theme_for_mood(self, mood: str) -> str:
        """Ask Dolphin LLM to select an appropriate theme based on the detected mood.
        
        Args:
            mood: The detected mood from the image
            
        Returns:
            Selected theme from available themes
        """
        available_themes = ", ".join(settings.SUPPORTED_THEMES)
        
        prompt = f"""Given the mood '{mood}' detected from a person's facial expression, 
        select the most appropriate story theme from these options: {available_themes}.
        Consider how this mood might influence the type of story someone would want to hear.
        Only respond with the exact theme name, nothing else."""
        
        try:
            async with self.session.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Ollama API error: {response.status}")
                
                result = await response.json()
                selected_theme = result.get("response", "").strip().lower()
                
                # Validate the selected theme
                if selected_theme not in settings.SUPPORTED_THEMES:
                    logger.warning(f"LLM selected invalid theme: {selected_theme}. Defaulting to 'comedy'")
                    selected_theme = "comedy"
                
                logger.info(f"\nSelected theme '{selected_theme}' based on mood '{mood}'\n")
                return selected_theme
                
        except Exception as e:
            logger.error(f"Error selecting theme for mood: {str(e)}")
            return "comedy"  # Default to comedy if there's an error
    
    async def generate_story(self, topics: List[str], theme: Optional[str] = None, mood: Optional[str] = None) -> Dict[str, Any]:
        """Generate a story based on trending topics and theme using Dolphin LLM.
        
        Args:
            topics: List of trending topics to include in the story
            theme: Optional theme of the story (if not provided, will be selected based on mood)
            mood: Optional mood to influence theme selection
            
        Returns:
            Dictionary containing the generated story and metadata
        """
        # Wait for initialization to complete if it's still in progress
        if not self.is_initialized:
            try:
                await self.init_task
            except Exception as e:
                # If the initialization task failed, try again
                logger.warning(f"\nInitialization task failed, retrying: {str(e)}\n")
                await self.initialize()
        
        # If mood is provided but theme isn't, select theme based on mood
        if mood and not theme:
            theme = await self.select_theme_for_mood(mood)
        elif not theme:
            theme = "comedy"  # Default theme if neither mood nor theme is provided
        
        # Format the prompt based on the theme only
        prompt_template = settings.PROMPT_TEMPLATES.get(
            theme, settings.PROMPT_TEMPLATES["default"]
        )
        
        topics_str = ", ".join(topics)
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Create the input text for Dolphin with current timestamp to prevent caching
        input_text = f"""Current time: {current_time}

{prompt_template.format(topics=topics_str, theme=theme)}

Remember:
	1.	Format: The story must be written in a storytelling/narrative style – not news style, listicle format, or plain exposition.
	2.	Content Source: Only use the given trend/topic as the story’s core inspiration. Do not introduce unrelated ideas or expand the scope.
	3.	Tense & Time: Keep the story grounded in the present moment. Do not mention future dates, events, or predictions.
	4.	Length: Keep the story short, concise, and complete — roughly 2–4 paragraphs max.
	5.	Uniqueness: Ensure every story is fresh — do not repeat structure, plot, or characters from any earlier story.
	6.	Structure: Make the story well-organized, with a clear beginning, middle, and end.
	7.	Complexity: Avoid oversimplification. Include at least one twist or unexpected turn to keep the reader hooked.
	8.	Tone: The story should feel alive, immersive, and engaging — like a mini screenplay or micro-drama.
	9.	Clarity: Ensure the plot is easy to follow, even when there’s a twist."""
        
        try:
            # Track generation time
            start_time = datetime.now(timezone.utc)
            
            # Make request to Ollama API with temperature for randomness
            async with self.session.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": input_text,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,  # Higher temperature for more randomness
                        "top_p": 0.9,        # Nucleus sampling for variety
                        "seed": int(time.time()),  # Random seed based on current time
                        "num_predict": 500   # Limit response length
                    }
                }
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Ollama API error: {response.status}")
                
                result = await response.json()
                generated_text = result.get("response", "")
            
            end_time = datetime.now(timezone.utc)
            generation_duration = (end_time - start_time).total_seconds()
            
            logger.info(f"\n\nStory generated in {generation_duration:.2f} seconds\n")
            
            # Create response with metadata - include original mood for reference
            response = {
                "story": generated_text,
                "metadata": {
                    "generation_time": end_time.isoformat(),
                    "generation_duration_seconds": generation_duration,
                    "model_name": self.model_name,
                    "theme": theme,
                    "original_mood": mood or "neutral",  # Store original mood that led to theme selection
                    "topics_used": topics
                }
            }
            
            return response
        except Exception as e:
            error_msg = f"Error generating story with Dolphin LLM: {str(e)}"
            logger.error(f"\n{error_msg}\n")
            raise RuntimeError(error_msg)
            
    async def __del__(self):
        """Cleanup the aiohttp session."""
        if self.session:
            await self.session.close()