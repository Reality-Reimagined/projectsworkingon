# backend/Dockerfile

# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    potrace \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create directories for uploads, processed images, and outputs
RUN mkdir -p uploads processed outputs logs

# Set permissions (optional, adjust as needed)
RUN chmod -R 755 uploads processed outputs logs

# Expose port
EXPOSE 8000

# Use a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser /app
USER appuser

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
