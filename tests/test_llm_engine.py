"""Unit tests for the LLM Engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from trendstory.llm_engine import LLMEngine

@pytest.fixture
def engine():
    return LLMEngine()

@pytest.fixture
def mock_topics():
    return ["Topic 1", "Topic 2", "Topic 3"]

@pytest.fixture
def theme():
    return "comedy"

@pytest.mark.asyncio
@patch('trendstory.llm_engine.T5Tokenizer.from_pretrained')
@patch('trendstory.llm_engine.T5ForConditionalGeneration.from_pretrained')
@patch('trendstory.llm_engine.pipeline')
async def test_initialize(mock_pipeline, mock_model, mock_tokenizer, engine):
    """Test T5 model initialization."""
    # Set up mocks
    mock_tokenizer.return_value = MagicMock()
    mock_model.return_value = MagicMock()
    mock_pipeline.return_value = MagicMock()
    
    # Call initialize
    await engine.initialize()
    
    # Verify mocks were called
    mock_tokenizer.assert_called_once()
    mock_model.assert_called_once()
    mock_pipeline.assert_called_once_with(
        "text2text-generation",
        model=mock_model.return_value,
        tokenizer=mock_tokenizer.return_value,
        device_map="auto"
    )
    
    # Verify engine state
    assert engine.is_initialized
    assert engine.tokenizer is not None
    assert engine.model is not None
    assert engine.generator is not None

@pytest.mark.asyncio
async def test_initialize_error(engine):
    """Test initialization error handling."""
    with patch('trendstory.llm_engine.T5Tokenizer.from_pretrained', 
              side_effect=Exception("Model not found")):
        with pytest.raises(RuntimeError):
            await engine.initialize()
        assert not engine.is_initialized

@pytest.mark.asyncio
async def test_generate_story(engine, mock_topics, theme):
    """Test story generation with T5."""
    # Set up engine with mocks
    engine.is_initialized = True
    engine.generator = MagicMock()
    engine.generator.return_value = [{
        "generated_text": "This is a test story."
    }]
    
    # Mock the initialize method
    engine.initialize = AsyncMock()
    
    # Call generate_story
    result = await engine.generate_story(mock_topics, theme)
    
    # Verify initialize was called
    engine.initialize.assert_called_once()
    
    # Verify generator was called with correct parameters
    engine.generator.assert_called_once()
    call_args = engine.generator.call_args[0]
    assert "Write a humorous and lighthearted story" in call_args[0]
    assert "Topic 1, Topic 2, Topic 3" in call_args[0]
    
    # Verify result structure
    assert "story" in result
    assert "metadata" in result
    assert result["story"] == "This is a test story."
    assert "generation_time" in result["metadata"]
    assert "model_name" in result["metadata"]
    assert "theme" in result["metadata"]
    assert "topics_used" in result["metadata"]
    assert result["metadata"]["theme"] == theme
    assert result["metadata"]["topics_used"] == mock_topics

@pytest.mark.asyncio
async def test_generate_story_error(engine, mock_topics, theme):
    """Test error handling during story generation."""
    engine.is_initialized = True
    engine.generator = MagicMock(side_effect=Exception("Generation error"))
    engine.initialize = AsyncMock()
    
    with pytest.raises(RuntimeError):
        await engine.generate_story(mock_topics, theme)
    engine.initialize.assert_called_once()

@pytest.mark.asyncio
async def test_generate_story_different_themes(engine, mock_topics):
    """Test story generation with different themes."""
    engine.is_initialized = True
    engine.generator = MagicMock()
    engine.generator.return_value = [{"generated_text": "Test story"}]
    engine.initialize = AsyncMock()
    
    themes = ["comedy", "tragedy", "sarcasm"]
    for theme in themes:
        result = await engine.generate_story(mock_topics, theme)
        assert result["metadata"]["theme"] == theme
        assert "Write a" in engine.generator.call_args[0][0]
        assert "story" in engine.generator.call_args[0][0]