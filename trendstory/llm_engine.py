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
        
        # Log start of initialization
        logger.info(f"\n\nStarting async initialization for model {self.model_name}...\n")
        
        # Start initialization asynchronously
        self.init_task = asyncio.create_task(self.initialize())
        
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
                logger.info(f"\n\nLoading T5 tokenizer from {self.model_name}...\n")
                tokenizer = await loop.run_in_executor(
                    None, 
                    lambda: T5Tokenizer.from_pretrained(
                        self.model_name, 
                        cache_dir=settings.MODEL_CACHE_DIR,
                        legacy=False,  # Use new tokenizer behavior
                        use_fast=True  # Use fast tokenizer
                    )
                )
                
                logger.info(f"\n\nLoading T5 model from {self.model_name}...\n")
                model = await loop.run_in_executor(
                    None,
                    lambda: T5ForConditionalGeneration.from_pretrained(
                        self.model_name,
                        cache_dir=settings.MODEL_CACHE_DIR,
                        device_map="auto"  # Use GPU if available
                    )
                )
                
                logger.info("\n\nCreating text generation pipeline...\n")
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
            
            # Log successful initialization and parameter count
            param_count = sum(p.numel() for p in self.model.parameters())
            logger.info(f"\n\nInitialized T5 model {self.model_name} with {param_count:,} parameters\n")
            
        except Exception as e:
            logger.error(f"\nError initializing T5 model: {str(e)}\n")
            raise RuntimeError(f"Failed to initialize T5 model: {str(e)}")
    
    async def generate_story(self, topics: List[str], theme: str) -> Dict[str, Any]:
        """Generate a story based on trending topics and theme using T5.
        
        Args:
            topics: List of trending topics to include in the story
            theme: The theme of the story
            
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
        
        # Format the prompt based on the theme
        prompt_template = settings.PROMPT_TEMPLATES.get(
            theme, settings.PROMPT_TEMPLATES["default"]
        )
        
        topics_str = ", ".join(topics)
        
        # Apply the summarize prefix to the prompt for better T5 generation
        input_text = f"{prompt_template.format(topics=topics_str, theme=theme)}"
        
        # # For, testing
        # input_text = f"Summarize: Write a trend story using the following trends context and the specified theme: Climate change affecting coastal cities, NASA's new space telescope discoveries, Top 10 upcoming video games in 2025, Celebrity news, Health and wellness tips, Latest tech innovations. Make it funny and witty."
        
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()

            # Use the text2text-generation pipeline for story generation
            logger.info(f"\n\nGenerating story with pipeline for theme '{theme}'...\n")
            
            # Track generation time
            start_time = datetime.now(timezone.utc)
            
            # Run generation via pipeline in executor
            result = await loop.run_in_executor(None, lambda: self.generator(
                input_text,
                max_length=300,
                num_beams=4,
                early_stopping=True
            ))
            # Extract generated text
            generated_text = result[0].get('generated_text', '')
            
            end_time = datetime.now(timezone.utc)
            generation_duration = (end_time - start_time).total_seconds()
            
            logger.info(f"\n\nStory generated in {generation_duration:.2f} seconds\n")
            
            # Create response with metadata
            response = {
                "story": generated_text,
                "metadata": {
                    "generation_time": end_time.isoformat(),
                    "generation_duration_seconds": generation_duration,
                    "model_name": self.model_name,
                    "theme": theme,
                    "topics_used": topics
                }
            }
            
            return response
        except Exception as e:
            error_msg = f"Error generating story with T5: {str(e)}"
            logger.error(f"\n{error_msg}\n")
            raise RuntimeError(error_msg)