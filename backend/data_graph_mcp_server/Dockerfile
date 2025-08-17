# Use the official Python lightweight image
FROM python:3.10-slim

# Install system dependencies for sentence_transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the project into /app
COPY . /app
WORKDIR /app

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Install dependencies system-wide (no virtual env)
RUN uv pip install --system -r requirements.txt

EXPOSE $PORT

# Run the FastMCP server
CMD ["python", "main.py"]
