# # backend/Dockerfile

# # Use official Python image as base
# FROM python:3.11-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libopencv-dev \
#     potrace \
#     && rm -rf /var/lib/apt/lists/*

# # Set work directory
# WORKDIR /app

# # Copy and install dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY main.py .

# # Create directories for uploads, processed images, and outputs
# RUN mkdir -p uploads processed outputs download logs

# # Set permissions (optional, adjust as needed)
# RUN chmod -R 755 uploads processed outputs logs

# # Expose port
# EXPOSE 8000

# # Use a non-root user for security
# RUN adduser --disabled-password --gecos '' appuser && \
#     chown -R appuser /app
# USER appuser

# # Run the application with Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


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

# Copy only requirements first to leverage docker cache
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Create necessary directories with correct permissions
RUN mkdir -p uploads processed outputs logs && \
    chown -R appuser:appuser uploads processed outputs logs

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Use a startup script or directly use uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
