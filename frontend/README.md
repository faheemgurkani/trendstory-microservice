# TrendStory Frontend

This is a detached frontend for the TrendStory microservice. It communicates with the backend via gRPC.

## Features

- Upload images for mood detection
- Generate stories based on trending topics
- Choose from multiple sources (YouTube, Google, or both)
- Select themes manually or let the system choose based on detected mood
- Download generated stories

## Prerequisites

- Python 3.8+
- Streamlit
- OpenCV
- gRPC
- PIL (Pillow)

## Getting Started

### Running with Docker (Recommended)

1. Make sure the TrendStory backend is running
2. Build and run the frontend container:
```bash
cd frontend
docker-compose up --build
```
3. Access the frontend at http://localhost:8501

### Running Locally

1. Install dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

2. Set the backend connection details:
```bash
# Create a .env file
echo "BACKEND_HOST=localhost" > .env
echo "BACKEND_PORT=50051" >> .env
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

4. Access the frontend at http://localhost:8501

## Configuration

You can configure the connection to the backend using environment variables:

- `BACKEND_HOST`: Hostname or IP address of the backend (default: localhost)
- `BACKEND_PORT`: gRPC port of the backend (default: 50051)

## gRPC Communication

This frontend is completely detached from the backend and communicates only through gRPC:

- `UploadImage`: Uploads images to the backend for processing
- `GenerateStory`: Generates stories based on provided parameters

No direct access to backend code or database is required.

## Architecture

The frontend is built as a separate application with its own Docker container, making it completely independent from the backend. This clean separation of concerns allows for easier maintenance and deployment.

```
┌───────────────┐           ┌───────────────┐
│               │           │               │
│   Frontend    │  ────►    │   Backend     │
│  (Streamlit)  │  gRPC     │  (TrendStory) │
│               │           │               │
└───────────────┘           └───────────────┘
``` 