# Use official Python image as base
FROM python:3.11-slim

# Set environment variables for better Python and pip behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    potrace \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Create a non-root user
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser

# Create necessary directories with correct permissions
RUN mkdir -p /app/uploads /app/processed /app/outputs /app/logs /app/download && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Copy only requirements first to leverage docker cache
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Ensure directories exist and have correct permissions after copy
RUN mkdir -p /app/uploads /app/processed /app/outputs /app/logs /app/download && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Use uvicorn with reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]