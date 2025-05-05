"""Unit tests for the LLM Engine (Dolphin LLM via Ollama API)."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from trendstory.llm_engine import LLMEngine

@pytest_asyncio.fixture
async def engine():
    return LLMEngine()

@pytest.fixture
def mock_topics():
    return ["Topic 1", "Topic 2", "Topic 3"]

@pytest.fixture
def theme():
    return "comedy"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_initialize_success(mock_session_cls, engine):
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.__aenter__.return_value = mock_response
    mock_session.post.return_value = mock_response
    mock_session.close = AsyncMock()
    mock_session_cls.return_value = mock_session

    await engine.initialize()
    assert engine.is_initialized
    assert engine.session is not None
    mock_session.post.assert_called_once()

@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_initialize_failure(mock_session_cls, engine):
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.__aenter__.return_value = mock_response
    mock_session.post.return_value = mock_response
    mock_session.close = AsyncMock()
    mock_session_cls.return_value = mock_session

    with pytest.raises(RuntimeError):
        await engine.initialize()
    assert not engine.is_initialized

@pytest.mark.asyncio
@patch.object(LLMEngine, "session", create=True)
async def test_select_theme_for_mood_success(mock_session, engine):
    engine.is_initialized = True
    mock_post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "comedy"})
    mock_post.return_value.__aenter__.return_value = mock_response
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    theme = await engine.select_theme_for_mood("happy")
    assert theme == "comedy"

@pytest.mark.asyncio
@patch.object(LLMEngine, "session", create=True)
async def test_select_theme_for_mood_invalid_theme(mock_session, engine):
    engine.is_initialized = True
    mock_post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "invalid_theme"})
    mock_post.return_value.__aenter__.return_value = mock_response
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    theme = await engine.select_theme_for_mood("angry")
    assert theme == "comedy"  # Defaults to comedy on invalid

@pytest.mark.asyncio
@patch.object(LLMEngine, "session", create=True)
async def test_select_theme_for_mood_error(mock_session, engine):
    engine.is_initialized = True
    mock_post = AsyncMock(side_effect=Exception("API error"))
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    theme = await engine.select_theme_for_mood("sad")
    assert theme == "comedy"  # Defaults to comedy on error

@pytest.mark.asyncio
@patch.object(LLMEngine, "session", create=True)
async def test_generate_story_success(mock_session, engine, mock_topics, theme):
    engine.is_initialized = True
    mock_post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "A generated story."})
    mock_post.return_value.__aenter__.return_value = mock_response
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    result = await engine.generate_story(mock_topics, theme)
    assert "story" in result
    assert result["story"] == "A generated story."
    assert "metadata" in result
    assert result["metadata"]["theme"] == theme
    assert result["metadata"]["topics_used"] == mock_topics

@pytest.mark.asyncio
@patch.object(LLMEngine, "session", create=True)
async def test_generate_story_error(mock_session, engine, mock_topics, theme):
    engine.is_initialized = True
    mock_post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={})
    mock_post.return_value.__aenter__.return_value = mock_response
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    with pytest.raises(RuntimeError):
        await engine.generate_story(mock_topics, theme)

@pytest.mark.asyncio
@patch.object(LLMEngine, "select_theme_for_mood", new_callable=AsyncMock)
@patch.object(LLMEngine, "session", create=True)
async def test_generate_story_with_mood(mock_session, mock_select_theme, engine, mock_topics):
    engine.is_initialized = True
    mock_select_theme.return_value = "comedy"
    mock_post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "A generated story."})
    mock_post.return_value.__aenter__.return_value = mock_response
    engine.session = AsyncMock(post=mock_post, close=AsyncMock())

    result = await engine.generate_story(mock_topics, theme=None, mood="happy")
    assert result["metadata"]["theme"] == "comedy"
    assert result["story"] == "A generated story."