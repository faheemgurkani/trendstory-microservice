# TrendStory Microservice

A microservice that generates themed stories based on trending topics from News API, with advanced mood detection capabilities using computer vision. The service uses gRPC for communication and integrates with Dolphin LLM via Ollama for story generation and emotion analysis.

## Features

- **Trend Analysis**
  - Current events and trending topics via News API
  - Category-based news fetching (business, technology, science, health, entertainment, sports, general)
  - Relevancy and popularity-based sorting
- **Advanced Mood Detection**
  - Facial expression recognition using DeepFace with RetinaFace backend
  - Real-time camera capture support
  - Background removal capabilities using rembg
  - Emotion mapping with confidence thresholds
  - Support for multiple face detection
- **Story Generation**
  - Integration with Dolphin LLM via Ollama API
  - Theme-based story generation (comedy, tragedy, sarcasm, mystery, romance, sci-fi)
  - Mood-influenced theme selection
  - Structured story generation with narrative guidelines
- **Multiple Interfaces**
  - gRPC server and client with async support
  - Rich terminal UI for interactive demos
  - Streamlit-based web interface
  - Camera capture interface for real-time mood detection

## Project Structure

```
trendstory-microservice/
├── trendstory/                # Core package
│   ├── llm_engine.py         # Dolphin LLM integration
│   ├── trends_fetcher.py     # News API integration
│   ├── mood_recognizer.py    # DeepFace emotion detection
│   ├── camera_capture.py     # OpenCV camera interface
│   ├── news_api_loader.py    # News API client
│   └── config.py             # Configuration management
├── proto/                     # gRPC protocol buffer definitions
├── frontend/                  # Streamlit web interface
├── tests/                    # Test suite
├── CAMERAPIC/               # Camera capture storage
├── model_cache/             # AI model cache
├── shared_uploads/          # Shared file storage
└── docs/                    # Documentation
```

## Prerequisites

- Python 3.8 or higher
- OpenCV compatible camera (for mood detection)
- Ollama server running locally (for LLM integration)
- News API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trendstory-microservice.git
cd trendstory-microservice
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

## Core Dependencies

- **AI and Image Processing**
  - deepface
  - opencv-python
  - rembg
  - retinaface

- **API Communication**
  - grpcio
  - aiohttp>=3.8.0
  - newsapi-python
  - httpx

- **Web Interface**
  - streamlit
  - rich (terminal UI)

- **Development Tools**
  - pytest suite
  - black
  - isort
  - flake8
  - mypy
  - pre-commit

## Running the Service

### 1. Start the Ollama Server
Ensure Ollama is running with the Dolphin model:
```bash
ollama run dolphin3
```

### 2. Start the gRPC Server
```bash
python grpc_server.py
```

### 3. Run the Web Interface
```bash
cd frontend
streamlit run app.py
```

### 4. Run the Demo Client (Optional)
```bash
python demo.py
```

The service will be available at:
- gRPC: localhost:50051
- Web Interface: localhost:8501
- Camera interface: Accessible through both web and demo interfaces

## Environment Variables

```env
# Server Configuration
TRENDSTORY_HOST=0.0.0.0
TRENDSTORY_PORT=50051

# API Keys
NEWS_API_KEY=your_news_api_key

# LLM Configuration
TRENDSTORY_MODEL_NAME=dolphin3:latest
TRENDSTORY_OLLAMA_API_URL=http://localhost:11434/api/generate

# Feature Flags
ENABLE_CAMERA_CAPTURE=true
ENABLE_MOOD_DETECTION=true
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run the pre-commit hooks
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.