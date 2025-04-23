"""Module for loading and using T5-small model to generate stories."""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline

from .config import settings

logger = logging.getLogger(__name__)

class LLMEngine:
    """Engine for text generation using T5-small model."""
    
    def __init__(self):
        """Initialize the LLM engine."""
        self.model_name = settings.MODEL_NAME
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the T5 model and tokenizer."""
        if self.is_initialized:
            return
            
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
            
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            
            async def load_model_and_tokenizer():
                tokenizer = await loop.run_in_executor(
                    None, 
                    lambda: T5Tokenizer.from_pretrained(
                        self.model_name, 
                        cache_dir=settings.MODEL_CACHE_DIR
                    )
                )
                
                model = await loop.run_in_executor(
                    None,
                    lambda: T5ForConditionalGeneration.from_pretrained(
                        self.model_name,
                        cache_dir=settings.MODEL_CACHE_DIR,
                        device_map="auto"  # Use GPU if available
                    )
                )
                
                generator = await loop.run_in_executor(
                    None,
                    lambda: pipeline(
                        "text2text-generation",
                        model=model,
                        tokenizer=tokenizer,
                        device_map="auto"
                    )
                )
                
                return tokenizer, model, generator
                
            self.tokenizer, self.model, self.generator = await load_model_and_tokenizer()
            self.is_initialized = True
            logger.info(f"Initialized T5 model {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing T5 model: {str(e)}")
            raise RuntimeError(f"Failed to initialize T5 model: {str(e)}")
    
    async def generate_story(self, topics: List[str], theme: str) -> Dict[str, Any]:
        """Generate a story based on trending topics and theme using T5.
        
        Args:
            topics: List of trending topics to include in the story
            theme: The theme of the story
            
        Returns:
            Dictionary containing the generated story and metadata
        """
        await self.initialize()
        
        # Format the prompt based on the theme
        prompt_template = settings.PROMPT_TEMPLATES.get(
            theme, settings.PROMPT_TEMPLATES["default"]
        )
        
        topics_str = ", ".join(topics)
        prompt = prompt_template.format(topics=topics_str, theme=theme)
        
        try:
            # Run generation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            generation_params = {
                "max_length": settings.MAX_NEW_TOKENS, 
                "temperature": settings.TEMPERATURE, 
                "do_sample": True,
                "top_p": 0.92,
                "top_k": 50,
                "repetition_penalty": 1.1
            }
            
            result = await loop.run_in_executor(
                None,
                lambda: self.generator(
                    prompt,
                    **generation_params
                )
            )
            
            # Extract generated text
            generated_text = result[0]["generated_text"]
            
            # Create response with metadata
            response = {
                "story": generated_text,
                "metadata": {
                    "generation_time": datetime.now(timezone.utc).isoformat(),
                    "model_name": self.model_name,
                    "theme": theme,
                    "topics_used": topics
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating story with T5: {str(e)}")
            raise RuntimeError(f"Failed to generate story: {str(e)}")