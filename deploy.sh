#!/bin/bash
set -e

# Configuration
SPACE_NAME="trendstory-microservice"
HF_USERNAME=${HF_USERNAME:-"your-username"}  # Override with env var if provided

echo "Deploying to Hugging Face Spaces: $HF_USERNAME/$SPACE_NAME"

# Check if Hugging Face token is available
if [ -z "$HF_TOKEN" ]; then
    echo "Error: HF_TOKEN environment variable is not set"
    exit 1
fi

# Create Docker image for Hugging Face
echo "Building Docker image for Hugging Face..."
docker build -t trendstory-microservice:latest .

# Save Docker image
echo "Saving Docker image..."
docker save trendstory-microservice:latest -o trendstory-image.tar

# Create a new Hugging Face Space if it doesn't exist
echo "Creating/updating Hugging Face Space..."
python - << EOF
from huggingface_hub import HfApi, SpaceStorage
import os

api = HfApi(token=os.environ["HF_TOKEN"])
username = "$HF_USERNAME"
space_name = "$SPACE_NAME"
space_id = f"{username}/{space_name}"

try:
    # Check if the space exists
    api.get_space_info(space_id)
    print(f"Space {space_id} already exists")
except Exception:
    # Create the space if it doesn't exist
    print(f"Creating new space: {space_id}")
    api.create_space(
        space_id,
        space_type="docker",
        private=False,
        sdk="docker",
    )

# Create Space README
readme_content = """
# TrendStory Microservice

A gRPC service that generates themed stories based on trending topics from various sources.

## Features

- Fetches trending topics from YouTube, TikTok, or Google
- Generates themed stories using a pre-trained language model
- Accessible via gRPC API

## API Usage

See the documentation in the repository for details on how to use the API.
"""

api.upload_file(
    path_or_fileobj=readme_content.encode(),
    path_in_repo="README.md",
    repo_id=space_id,
    repo_type="space",
)

print(f"Uploaded README to {space_id}")
EOF

# Upload Docker image to Hugging Face Space
echo "Uploading Docker image to Hugging Face Space..."
python - << EOF
from huggingface_hub import HfApi
import os

api = HfApi(token=os.environ["HF_TOKEN"])
username = "$HF_USERNAME"
space_name = "$SPACE_NAME"
space_id = f"{username}/{space_name}"

# Upload Docker image
with open("trendstory-image.tar", "rb") as f:
    api.upload_file(
        path_or_fileobj=f,
        path_in_repo="image.tar",
        repo_id=space_id,
        repo_type="space",
    )

print(f"Uploaded Docker image to {space_id}")

# Update space to use Docker image
api.upload_file(
    path_or_fileobj=b"""
sdk: docker
dockerfile: false
base_image: image.tar
""",
    path_in_repo="README.md",
    repo_id=space_id,
    repo_type="space",
)

print(f"Updated space configuration at {space_id}")
EOF

# Clean up
echo "Cleaning up..."
rm trendstory-image.tar

echo "Deployment to Hugging Face Spaces completed successfully!"