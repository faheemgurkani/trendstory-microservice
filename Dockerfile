# Multi-stage build
# Stage 1: Build dependencies and proto files
FROM python:3.10-slim AS builder

WORKDIR /app

# Install protobuf compiler
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    protobuf-compiler \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ proto/

# Generate Python code from proto
RUN mkdir -p proto && \
    python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    proto/trendstory.proto

# Stage 2: Runtime image
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRENDSTORY_HOST=0.0.0.0 \
    TRENDSTORY_PORT=50051

# Install runtime dependencies
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy generated protobuf files
COPY --from=builder /app/proto/ /app/proto/

# Copy application code
COPY trendstory/ /app/trendstory/
COPY tests/ /app/tests/
COPY requirements.txt README.md ./

# Create model cache directory
RUN mkdir -p /tmp/trendstory/models && \
    chmod -R 777 /tmp/trendstory

# Expose port for gRPC
EXPOSE 50051

# Run the application
CMD ["python", "-m", "trendstory.main"]