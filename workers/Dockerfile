FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY app/ ./app/

# Run Celery worker
CMD ["celery", "-A", "app.main.celery_app", "worker", "--loglevel=info"]
