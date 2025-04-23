from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trendstory-microservice",
    version="0.1.0",
    author="Trendstory Team",
    author_email="info@trendstory.ai",
    description="A microservice that generates themed stories based on trending topics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trendstory-microservice",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/trendstory-microservice/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.10",
    install_requires=[
        "grpcio>=1.57.0",
        "grpcio-tools>=1.57.0",
        "grpcio-reflection>=1.57.0",
        "protobuf>=4.24.0",
        "pydantic>=2.3.0",
        "python-dotenv>=1.0.0",
        "google-api-python-client>=2.95.0",
        "pytrends>=4.9.2",
        "torch>=2.0.1",
        "transformers>=4.35.0",
        "accelerate>=0.23.0",
        "huggingface-hub>=0.16.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "mypy>=1.5.0",
        ],
        "frontend": [
            "streamlit>=1.25.0",
        ],
        "performance": [
            "locust>=2.15.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "trendstory-server=trendstory.main:main",
            "trendstory-client=trendstory.client:main",
        ],
    },
    include_package_data=True,
    package_data={
        "proto": ["*.proto"],
    },
)