#!/usr/bin/env python3
"""Demo script to visualize the TrendStory microservice workflow."""

import asyncio
import sys
import warnings
import os
from typing import Dict, List

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress HuggingFace symlink warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning, module='huggingface_hub')
warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
warnings.filterwarnings('ignore', category=FutureWarning)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from trendstory.trends_fetcher import TrendsFetcher
from trendstory.llm_engine import LLMEngine
from trendstory.config import settings

console = Console()

def display_header():
    """Display the application header."""
    console.print(Panel.fit(
        "[bold blue]TrendStory Microservice Demo[/bold blue]\n"
        "Generate themed stories from trending topics",
        border_style="blue"
    ))

def display_themes() -> str:
    """Display available themes and get user selection."""
    table = Table(title="Available Themes", show_header=True, header_style="bold magenta")
    table.add_column("Theme", style="cyan")
    table.add_column("Description", style="green")
    
    theme_descriptions = {
        "comedy": "Humorous and lighthearted stories",
        "tragedy": "Sad and emotional stories",
        "sarcasm": "Sarcastic and ironic stories",
        "mystery": "Suspenseful mystery stories",
        "romance": "Romantic stories",
        "sci-fi": "Science fiction stories"
    }
    
    for theme, desc in theme_descriptions.items():
        table.add_row(theme, desc)
    
    console.print(table)
    
    while True:
        theme = Prompt.ask(
            "\n[bold]Select a theme[/bold]",
            choices=list(theme_descriptions.keys()),
            default="comedy"
        )
        return theme

def display_trends(youtube_trends: List[str], google_trends: List[str]):
    """Display the fetched trends in a formatted table."""
    table = Table(title="Fetched Trends", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="cyan")
    table.add_column("Trending Topics", style="green")
    
    table.add_row("YouTube", "\n".join(f"• {topic}" for topic in youtube_trends))
    table.add_row("Google Trends", "\n".join(f"• {topic}" for topic in google_trends))
    
    console.print(table)

def display_story(story_data: Dict):
    """Display the generated story with metadata."""
    console.print("\n[bold blue]Generated Story[/bold blue]")
    console.print(Panel.fit(
        story_data["story"],
        title="Story",
        border_style="blue"
    ))
    
    metadata = story_data["metadata"]
    console.print("\n[bold blue]Story Metadata[/bold blue]")
    console.print(f"• Theme: [cyan]{metadata['theme']}[/cyan]")
    console.print(f"• Model: [cyan]{metadata['model_name']}[/cyan]")
    console.print(f"• Generation Time: [cyan]{metadata['generation_time']}[/cyan]")
    console.print("\n[bold]Topics Used:[/bold]")
    for topic in metadata["topics_used"]:
        console.print(f"• [green]{topic}[/green]")

async def main():
    """Main demo function."""
    display_header()
    
    # Initialize components
    trends_fetcher = TrendsFetcher()
    llm_engine = LLMEngine()
    
    # Get user theme selection
    theme = display_themes()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Fetch trends
        progress.add_task(description="Fetching YouTube trends...", total=None)
        youtube_trends = await trends_fetcher.fetch_trends("youtube", limit=3)
        
        progress.add_task(description="Fetching Google Trends...", total=None)
        google_trends = await trends_fetcher.fetch_trends("google", limit=3)
        
        # Display trends
        display_trends(youtube_trends, google_trends)
        
        # Generate story
        progress.add_task(description="Generating story...", total=None)
        story_data = await llm_engine.generate_story(
            topics=youtube_trends + google_trends,
            theme=theme
        )
        
        # Display story
        display_story(story_data)
    
    # Ask if user wants to generate another story
    if Confirm.ask("\n[bold]Would you like to generate another story?[/bold]"):
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Demo interrupted by user[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1) 