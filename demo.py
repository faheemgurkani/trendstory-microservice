#!/usr/bin/env python3
"""Demo script to visualize the TrendStory microservice workflow."""

import asyncio
import sys
import warnings
import os
import time
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trendstory-demo")

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress HuggingFace symlink warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning, module='huggingface_hub')
warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*legacy behaviour of the.*T5Tokenizer.*')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.status import Status
from rich import print as rprint
from rich.layout import Layout
from rich.text import Text
from rich.box import ROUNDED

from trendstory.trends_fetcher import TrendsFetcher
from trendstory.llm_engine import LLMEngine
from trendstory.config import settings

console = Console()

def display_header():
    """Display the application header."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]TrendStory Microservice Demo[/bold blue]\n"
        "[dim]Generate themed stories from trending topics[/dim]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print("\n")

def display_themes() -> str:
    """Display available themes and get user selection."""
    # console.print("\n")
    table = Table(
        title="[bold magenta]Available Themes[/bold magenta]",
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        padding=(0, 1)
    )
    table.add_column("Theme", style="cyan", width=10)
    table.add_column("Description", style="green", width=40)
    
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
    # console.print("\n")
    
    while True:
        theme = Prompt.ask(
            "[bold]Select a theme[/bold]",
            choices=list(theme_descriptions.keys()),
            default="comedy"
        )
        return theme

def display_trends(youtube_trends: List[str], google_trends: List[str], youtube_status="", google_status=""):
    """Display the fetched trends in a formatted table."""
    # console.print("\n")
    table = Table(
        title="[bold magenta]Fetched Trends[/bold magenta]",
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        padding=(0, 1)
    )
    table.add_column("Source", style="cyan", width=15)
    table.add_column("Trending Topics", style="green", width=40)
    table.add_column("Status", style="yellow", width=20)
    
    # Format YouTube trends
    youtube_topics = "\n".join(f"• {topic}" for topic in youtube_trends)
    table.add_row(
        "YouTube",
        youtube_topics,
        youtube_status or "✓ Ready"
    )
    
    # Format Google trends
    google_topics = "\n".join(f"• {topic}" for topic in google_trends)
    table.add_row(
        "Google Trends",
        google_topics,
        google_status or "✓ Ready"
    )
    
    console.print(table)
    # console.print("\n")

def display_story(story_data: Dict):
    """Display the generated story with metadata."""
    # console.print("\n")
    
    # Story panel
    story_panel = Panel.fit(
        story_data["story"],
        title="[bold blue]Generated Story[/bold blue]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(story_panel)
    
    # Metadata table
    metadata = story_data["metadata"]
    meta_table = Table(
        title="[bold blue]Story Metadata[/bold blue]",
        show_header=False,
        box=ROUNDED,
        padding=(0, 1)
    )
    meta_table.add_column("Field", style="cyan", width=20)
    meta_table.add_column("Value", style="green", width=40)
    
    meta_table.add_row("Theme", metadata['theme'])
    meta_table.add_row("Model", metadata['model_name'])
    
    if 'generation_duration_seconds' in metadata:
        meta_table.add_row(
            "Generation Time",
            f"{metadata['generation_duration_seconds']:.2f} seconds"
        )
    else:
        gen_time = metadata['generation_time']
        if 'T' in gen_time:
            gen_time = gen_time.split('T')[1].split('.')[0]
        meta_table.add_row("Generation Time", gen_time)
    
    # console.print("\n")
    console.print(meta_table)
    
    # Topics used
    console.print("\n[bold]Topics Used:[/bold]")
    for topic in metadata["topics_used"]:
        console.print(f"  • [green]{topic}[/green]")
    # console.print("\n")

async def main():
    """Main demo function."""
    start_time = time.time()
    logger.info("\nStarting TrendStory demo")
    display_header()
    
    try:
        # Initialize components
        logger.info("\nCreating TrendsFetcher and LLMEngine instances\n")
        trends_fetcher = TrendsFetcher()
        llm_engine = LLMEngine()
        
        # Show initialization status
        with Status("[bold blue]Initializing LLM engine...[/bold blue]") as status:
            await asyncio.sleep(0.5)
            
            for _ in range(3):
                if llm_engine.is_initialized:
                    break
                await asyncio.sleep(1)
                status.update("[bold blue]Still initializing LLM engine (this may take a minute)...[/bold blue]")
        
        if llm_engine.is_initialized:
            console.print("[green]✓[/green] LLM engine initialized\n")
        else:
            console.print("[yellow]![/yellow] LLM engine initializing in background...\n")
        
        # Get user theme selection
        theme = display_themes()
        logger.info(f"\nUser selected theme: {theme}\n")
        
        youtube_trends = []
        google_trends = []
        youtube_status = ""
        google_status = ""
        
        # Fetch YouTube trends
        with Status("[bold blue]Fetching YouTube trends...[/bold blue]") as status:
            try:
                logger.info("\nFetching YouTube trends\n")
                fetch_start = time.time()
                youtube_trends = await trends_fetcher.fetch_trends("youtube", limit=3)
                fetch_time = time.time() - fetch_start
                logger.info(f"YouTube trends fetched in {fetch_time:.2f}s: {youtube_trends}\n")
                youtube_status = f"✓ Fetched in {fetch_time:.2f}s"
                console.print(f"[green]✓[/green] YouTube trends fetched\n")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error fetching YouTube trends: {error_msg}\n")
                console.print(f"[red]✗[/red] Error fetching YouTube trends: {error_msg}\n")
                youtube_status = f"✗ Error: {error_msg}"
        
        # Fetch Google trends
        with Status("[bold blue]Fetching Google trends...[/bold blue]") as status:
            try:
                logger.info("\nFetching Google trends\n")
                fetch_start = time.time()
                google_trends = await trends_fetcher.fetch_trends("google", limit=3)
                fetch_time = time.time() - fetch_start
                logger.info(f"\nGoogle trends fetched in {fetch_time:.2f}s: {google_trends}\n")
                google_status = f"✓ Fetched in {fetch_time:.2f}s"
                console.print(f"\n[green]✓[/green] Google trends fetched\n")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"\nError fetching Google trends: {error_msg}\n")
                console.print(f"\n[red]✗[/red] Error fetching Google trends: {error_msg}\n")
                google_status = f"✗ Error: {error_msg}"
                
                try:
                    google_trends = await trends_fetcher._get_mock_google_trends(3)
                    google_status = "! Using mock data"
                    console.print("\n[yellow]![/yellow] Using mock Google trends data\n")
                except Exception as e2:
                    logger.error(f"\nError getting mock Google trends: {str(e2)}\n")
        
        # Display trends with status information
        display_trends(youtube_trends, google_trends, youtube_status, google_status)
        
        # Combine all topics
        all_topics = youtube_trends + google_trends
        
        if not all_topics:
            console.print("\n[red]No topics available to generate a story![/red]\n")
            return
        
        # Generate story
        with Status("[bold blue]Generating story...[/bold blue]") as status:
            try:
                logger.info(f"\nGenerating story with theme '{theme}' and topics: {all_topics}\n")
                gen_start = time.time()
                
                if not llm_engine.is_initialized:
                    status.update("[bold blue]Waiting for LLM engine to initialize...[/bold blue]")
                    await asyncio.wait_for(llm_engine.init_task, timeout=60)
                    status.update("[bold blue]Generating story...[/bold blue]")
                
                story_data = await llm_engine.generate_story(
                    topics=all_topics,
                    theme=theme
                )
                
                gen_time = time.time() - gen_start
                logger.info(f"Story generated in {gen_time:.2f}s")
                console.print(f"\n[green]✓[/green] Story generated in {gen_time:.2f}s\n")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"\nError generating story: {error_msg}\n")
                console.print(f"\n[red]✗[/red] Error generating story: {error_msg}\n")
                raise
        
        # Display story
        display_story(story_data)
        
        total_time = time.time() - start_time
        logger.info(f"\nDemo completed in {total_time:.2f}s\n")
        console.print(Panel.fit(
            f"[bold green]Demo completed in {total_time:.2f} seconds[/bold green]",
            border_style="green",
            box=ROUNDED
        ))
        # console.print("\n")
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"\nDemo error: {error_msg}\n")
        console.print(Panel.fit(
            f"[bold red]Error: {error_msg}[/bold red]\n"
            "[yellow]Please try again with a different theme or restart the application.[/yellow]",
            border_style="red",
            box=ROUNDED
        ))
        return
    
    # Ask if user wants to generate another story
    if Confirm.ask("\n[bold]Would you like to generate another story?[/bold]"):
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user\n")
        console.print("\n[bold red]Demo interrupted by user[/bold red]\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nUnhandled exception: {str(e)}\n")
        console.print(f"\n[bold red]Unhandled error: {str(e)}[/bold red]\n")
        sys.exit(1) 