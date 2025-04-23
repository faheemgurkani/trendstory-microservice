# TrendStory Architecture

This document outlines the high-level architecture of the TrendStory microservice.

## Overview

TrendStory is a gRPC-based microservice that generates themed stories based on trending topics from various sources. The system follows a modular design with clear separation of concerns to ensure maintainability and testability.

## System Components

### 1. gRPC API Layer

The gRPC API layer defines the contract between clients and the service using Protocol Buffers. The core functionality is exposed through a single RPC method:

```protobuf
rpc Generate(GenerateRequest) returns (GenerateResponse)
```

This layer is implemented in `main.py` which sets up the gRPC server and registers the service implementation.

### 2. Service Layer

The service layer (`service.py`) contains the business logic that:
- Validates incoming requests
- Coordinates between the trends fetcher and LLM engine
- Handles errors and returns appropriate responses

### 3. Trends Fetcher Module

The trends fetcher (`trends_fetcher.py`) is responsible for:
- Fetching trending topics from various sources (YouTube, TikTok, Google)
- Normalizing the data from different sources
- Handling API rate limits and errors

### 4. LLM Engine Module

The LLM engine (`llm_engine.py`) is responsible for:
- Loading and managing the language model
- Constructing appropriate prompts based on the trending topics and desired theme
- Generating coherent stories using the language model
- Optimizing for performance and output quality

## Data Flow

```
┌───────────┐     ┌───────────┐     ┌────────────┐     ┌────────────┐
│  Client   │────▶│   gRPC    │────▶│  Service   │────▶│   Trends   │
│  Request  │     │  Server   │     │   Layer    │     │  Fetcher   │
└───────────┘     └───────────┘     └────────────┘     └────────────┘
                                          │                  │
                                          │                  │
                                          ▼                  ▼
                                    ┌────────────┐    ┌────────────┐
                                    │    LLM     │◀───│  Trending  │
                                    │   Engine   │    │   Topics   │
                                    └────────────┘    └────────────┘
                                          │
                                          │
                                          ▼
                                    ┌────────────┐
                                    │  Generated │
                                    │   Story    │
                                    └────────────┘
```

## Asynchronous Design

The system leverages Python's async/await features for improved performance:

1. gRPC server uses `grpc.aio` for asynchronous request handling
2. Trend fetching operations are performed asynchronously
3. LLM inference is wrapped in async functions to prevent blocking

## Error Handling Strategy

The service employs a robust error handling approach:

1. Input validation using Pydantic models
2. Graceful handling of external API failures
3. Proper gRPC status codes for different error scenarios
4. Detailed error messages for debugging
5. Automatic retries for transient failures

## Deployment Architecture

The service is designed to be deployed as a container with the following characteristics:

1. Lightweight Docker image
2. Environment variable configuration
3. Health check endpoints
4. Metrics for monitoring (optional)
5. Seamless integration with Hugging Face Spaces

## Security Considerations

1. API keys are stored as environment variables
2. No sensitive data is logged
3. Input sanitization to prevent prompt injection
4. Rate limiting to prevent abuse

## Future Enhancements

1. Caching layer for trending topics
2. Multiple language model support
3. Content moderation for generated stories
4. Streaming response support