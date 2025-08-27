# AI-Driven Digital Twin Demo for SNIA SDC 2025
# Using Azure OpenAI GPT-4 for device generation
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output/recordings

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from config import Config; print('Health check passed')" || exit 1

# Default command - can be overridden at runtime
CMD ["python", "demo_fixed.py"]

# Usage examples:
# docker run --rm -it -e AZURE_OPENAI_API_KEY=your_key -e AZURE_OPENAI_ENDPOINT=your_endpoint digital-twin-demo
# docker run --rm -it -e AZURE_OPENAI_API_KEY=your_key -e AZURE_OPENAI_ENDPOINT=your_endpoint digital-twin-demo python main.py
