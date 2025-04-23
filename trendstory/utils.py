"""Utility functions for TrendStory microservice."""

import os
import sys
import logging
import time
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def time_execution(func):
    """Decorator to measure function execution time.
    
    Args:
        func: The function to time
        
    Returns:
        Wrapped function that logs execution time
    """
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.debug(f"{func.__name__} executed in {duration:.2f} seconds")
        return result
        
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.debug(f"{func.__name__} executed in {duration:.2f} seconds")
        return result
    
    # Return appropriate wrapper based on if func is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def sanitize_output(text: str) -> str:
    """Sanitize output text to remove potential harmful content.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    # Basic sanitization - remove any script tags
    sanitized = text.replace("<script>", "").replace("</script>", "")
    return sanitized


def format_error_response(error_message: str) -> Dict[str, Any]:
    """Format an error response.
    
    Args:
        error_message: The error message
        
    Returns:
        Formatted error response dictionary
    """
    return {
        "status_code": 1,  # Non-zero indicates error
        "error_message": error_message,
        "story": "",
        "topics_used": [],
        "metadata": {
            "generation_time": datetime.now(timezone.utc).isoformat(),
            "model_name": "",
            "source": "",
            "theme": ""
        }
    }


def validate_theme(theme: str, supported_themes: List[str]) -> str:
    """Validate and normalize the requested theme.
    
    Args:
        theme: The requested theme
        supported_themes: List of supported themes
        
    Returns:
        Normalized theme name or 'default' if invalid
        
    Raises:
        ValueError: If theme is invalid and strict validation is enabled
    """
    normalized = theme.lower().strip()
    
    if not normalized or normalized not in supported_themes:
        return "default"
    
    return normalized


async def retry_async(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries (seconds)
        backoff_factor: Backoff multiplier
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Result of the function
        
    Raises:
        The last exception if all retries fail
    """
    retries = 0
    current_delay = delay
    
    while True:
        try:
            return await func()
        except exceptions as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Failed after {max_retries} retries: {str(e)}")
                raise
            
            logger.warning(f"Retry {retries}/{max_retries} after {current_delay:.2f}s due to: {str(e)}")
            await asyncio.sleep(current_delay)
            current_delay *= backoff_factor