import os
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict

from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pyembroidery import *
from svgpathtools import svg2paths, Path as SvgPath, Line
from PIL import Image, ImageFilter
import cv2
import numpy as np
import logging
import asyncio
import math

# ---------------------
# Configuration
# ---------------------

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
DOWNLOAD_DIR = BASE_DIR / "download"

# Create directories if they don't exist and ensure proper permissions
def ensure_directories():
    directories = [UPLOAD_DIR, PROCESSED_DIR, OUTPUT_DIR, LOG_DIR, DOWNLOAD_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        # Ensure directory has proper permissions (755)
        try:
            directory.chmod(0o755)
        except Exception as e:
            logging.warning(f"Could not set permissions for {directory}: {e}")

# Initialize directories
ensure_directories()

# Logging configuration
logging.basicConfig(
    filename=LOG_DIR / "digitization.log",
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

[... rest of the file remains the same ...]

@app.post("/upload/", response_model=UploadResponse)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    client_id: str = Form(...),
    stitch_density: int = Form(default=2),
    stitch_type: str = Form(default="normal")
):
    """
    Endpoint to upload an image and receive the embroidered DST file.
    """
    # Ensure directories exist
    ensure_directories()
    
    logging.info(f"Received upload request - client_id: {client_id}, stitch_density: {stitch_density}, stitch_type: {stitch_type}")

    try:
        # Validate file type
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

        # Limit file size (10 MB)
        max_file_size = 10 * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_file_size:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        await file.seek(0)

        # Generate unique filename and save file
        unique_filename = get_unique_filename(file.filename)
        upload_path = UPLOAD_DIR / unique_filename
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Prepare settings
        settings = {
            "stitch_density": stitch_density,
            "stitch_type": stitch_type
        }

        logging.info(f"File saved to {upload_path}, starting digitization with settings: {settings}")

        # Start digitization in background
        background_tasks.add_task(digitize_image, client_id, upload_path, settings)

        # Generate download URL
        download_url = f"/download/{unique_filename.split('.')[0]}.dst"

        return UploadResponse(
            filename=unique_filename.split('.')[0] + ".dst",
            download_url=download_url,
            message="Embroidery file is being created. Check updates via WebSocket."
        )

    except Exception as e:
        logging.error(f"Error in upload_image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    """
    Endpoint to download the generated DST file.
    """
    # Ensure directories exist
    ensure_directories()
    
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        logging.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found.")
    
    try:
        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=filename
        )
    except Exception as e:
        logging.error(f"Error serving file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error serving file")

[... rest of the file remains the same ...]