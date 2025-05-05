# TrendStory Microservice Architecture

## System Overview

TrendStory is a sophisticated microservice-based application that combines trending news analysis, mood detection, and AI-powered story generation. The system is built using a modular architecture that emphasizes scalability, maintainability, and real-time processing capabilities.

## Architecture Diagram

```
+----------------------------------------------------------------------------------------+
|                                  External Services                                      |
|  +----------------+                                        +----------------------+      |
|  |    News API    |                                       |   Ollama LLM Service |      |
|  +----------------+                                        +----------------------+      |
|         ▲                                                           ▲                   |
|         |                                                           |                   |
+---------|------------------------------------------------------|-------------------+   |
          |                                                        |                      |
          |                     Core Services                      |                      |
          |            +--------------------------------+          |                      |
          |            |                                |          |                      |
          |      +------------+                  +-----------+     |                      |
          |      |            |                  |           |     |                      |
          +------| Trends     |                  |   LLM     |-----+                      |
                 | Fetcher    |                  |   Engine  |                            |
                 |            |                  |           |                            |
                 +------------+                  +-----------+                            |
                      ▲                              ▲                                    |
                      |                              |                                    |
                 +------------------------------------+                                   |
                 |         gRPC Server                |                                   |
                 +------------------------------------+                                   |
                      ▲                              ▲                                    |
                      |                              |                                    |
                 +------------+                 +------------+                            |
                 |   Mood    |                 |  Camera   |                            |
                 |Recognizer |◄────────────────| Capture   |                            |
                 +------------+                 +------------+                            |
                      ▲                              ▲                                    |
                      |                              |                                    |
          +----------|------------------------------|--------------------+                |
          |          |          Storage             |                   |                |
          |     +------------+                 +------------+           |                |
          |     |   Model   |                 |  Camera   |           |                |
          |     |   Cache   |                 | Pictures  |           |                |
          |     +------------+                 +------------+           |                |
          |                                                            |                |
          +------------------------------------------------------------+                |
                                     ▲                                                   |
                                     |                                                   |
                              +------------+                                             |
                              |    Web    |                                             |
                              |Interface  |                                             |
                              +------------+                                             |
                                     ▲                                                   |
                                     |                                                   |
                              +------------+                                             |
                              |  Client   |                                             |
                              |  Browser  |                                             |
                              +------------+                                             |
```

## Component Description

### 1. Core Services

#### gRPC Server
- Primary communication hub for all service interactions
- Handles request routing and service orchestration
- Implements async operations for improved performance
- Manages concurrent client connections

#### Web Interface (Streamlit)
- Provides user-friendly web access to all features
- Real-time camera integration
- Interactive story generation interface
- Trend visualization and mood detection results display

### 2. TrendStory Core Components

#### Trends Fetcher
- Integrates with News API
- Categorizes and filters trending topics
- Implements caching for improved performance
- Supports multiple news categories

#### Mood Recognizer
- Uses DeepFace with RetinaFace backend
- Real-time facial expression analysis
- Multi-face detection support
- Emotion confidence scoring
- Background removal capabilities

#### LLM Engine
- Integrates with Dolphin LLM via Ollama
- Theme-based story generation
- Context-aware content creation
- Mood-influenced narrative adaptation

#### Camera Capture
- OpenCV-based camera interface
- Real-time image processing
- Frame buffering and optimization
- Multiple camera support

### 3. Storage Systems

#### Model Cache
- Stores AI model weights and configurations
- Caches frequently used models
- Optimizes model loading times

#### Shared Uploads
- Manages user-uploaded content
- Temporary storage for processing
- File cleanup management

#### Camera Pictures
- Stores captured images
- Manages image processing results
- Temporary storage for mood detection

## Communication Flow

1. **Client Requests**
   - gRPC clients connect to the server
   - Web interface provides REST-like access
   - Both synchronous and asynchronous operations supported

2. **Data Processing**
   - Trends are fetched and analyzed
   - Images are processed for mood detection
   - Stories are generated based on trends and mood

3. **Response Handling**
   - Results are formatted and returned to clients
   - Real-time updates for camera-based features
   - Cached responses for improved performance

## Security Considerations

- API keys stored in environment variables
- Secure gRPC communication
- Rate limiting on API endpoints
- Input validation and sanitization
- Temporary file cleanup procedures

## Scalability Features

- Microservice architecture allows independent scaling
- Async operations for improved concurrency
- Caching mechanisms for frequently accessed data
- Modular design for easy feature addition

## Development and Deployment

- Docker containerization support
- Environment-based configuration
- Comprehensive testing suite
- CI/CD pipeline integration
- Monitoring and logging capabilities