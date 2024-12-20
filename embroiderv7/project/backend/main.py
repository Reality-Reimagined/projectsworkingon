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

# # ---------------------
# # Configuration
# # ---------------------

# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# PROCESSED_DIR = BASE_DIR / "processed"
# OUTPUT_DIR = BASE_DIR / "outputs"
# LOG_DIR = BASE_DIR / "logs"

# # Create directories if they don't exist
# for directory in [UPLOAD_DIR, PROCESSED_DIR, OUTPUT_DIR, LOG_DIR]:
#     directory.mkdir(parents=True, exist_ok=True)

# # Logging configuration
# logging.basicConfig(
#     filename=LOG_DIR / "digitization.log",
#     level=logging.INFO,
#     format='%(asctime)s:%(levelname)s:%(message)s'
# )


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


# ---------------------
# FastAPI App Initialization
# ---------------------

app = FastAPI(
    title="Embroidery Digitization API",
    description="API for converting images to embroidery files (DST)",
    version="1.0.0"
)

# Allow CORS for frontend interaction
origins = [
    "http://localhost",
    "http://localhost:3000",
    "*",  # React default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# WebSocket Manager
# ---------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # client_id: WebSocket

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logging.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logging.info(f"WebSocket disconnected: {client_id}")

    async def send_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
            logging.info(f"Sent message to {client_id}: {message}")

manager = ConnectionManager()

# ---------------------
# Pydantic Schemas
# ---------------------

class UploadResponse(BaseModel):
    filename: str
    download_url: str
    message: Optional[str] = "Embroidery file created successfully."

class DigitizationSettings(BaseModel):
    stitch_density: Optional[int] = 10  # Example setting

# ---------------------
# Utility Functions
# ---------------------

def get_unique_filename(filename: str) -> str:
    """Generate a unique filename to prevent overwriting."""
    unique_id = uuid.uuid4().hex
    base, ext = os.path.splitext(filename)
    return f"{base}_{unique_id}{ext}"

# ---------------------
# Digitization Functions
# ---------------------

async def preprocess_image(image_path: Path) -> Path:
    """
    Preprocess the image: convert to grayscale, resize, and apply thresholding.
    Save the processed image as a BMP file for Potrace.
    """
    try:
        image = Image.open(image_path).convert('L')  # Convert to grayscale
        image = image.resize((500, 500))  # Resize as needed
        image = image.filter(ImageFilter.GaussianBlur(radius=1))  # Noise reduction
        image_np = np.array(image)

        # Apply adaptive thresholding for better results
        thresh = cv2.adaptiveThreshold(
            image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        processed_filename = image_path.stem + "_processed.bmp"
        processed_path = PROCESSED_DIR / processed_filename
        cv2.imwrite(str(processed_path), thresh)
        logging.info(f"Image preprocessed and saved to {processed_path}")
        return processed_path
    except Exception as e:
        logging.error(f"Error in preprocess_image: {e}")
        raise e

def vectorize_image(processed_image_path: Path) -> Path:
    """
    Vectorize the processed bitmap image using Potrace via command line.
    Save the output as an SVG file.
    """
    try:
        svg_filename = processed_image_path.stem + ".svg"
        svg_path = PROCESSED_DIR / svg_filename

        # Call Potrace to convert BMP to SVG
        subprocess.run(
            ['potrace', str(processed_image_path), '-s', '-o', str(svg_path)],
            check=True
        )
        logging.info(f"Vector image saved to {svg_path}")
        return svg_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Potrace failed: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error in vectorize_image: {e}")
        raise e

def perpendicular_distance(point, start, end):
    """
    Calculate the perpendicular distance from a point to a line segment.
    """
    if start == end:
        return math.hypot(point.real - start.real, point.imag - start.imag)
    else:
        n = abs((end.real - start.real) * (start.imag - point.imag) - 
                (start.real - point.real) * (end.imag - start.imag))
        d = math.hypot(end.real - start.real, end.imag - start.imag)
        return n / d

def rdp(points, epsilon):
    """
    Ramer-Douglas-Peucker algorithm to simplify points.
    """
    dmax = 0.0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        d = perpendicular_distance(points[i], points[0], points[end])
        if d > dmax:
            index = i
            dmax = d
    if dmax > epsilon:
        rec_results1 = rdp(points[:index+1], epsilon)
        rec_results2 = rdp(points[index:], epsilon)
        result = rec_results1[:-1] + rec_results2
    else:
        result = [points[0], points[end]]
    return result

def simplify_paths(paths, tolerance=2.0):
    """
    Simplify SVG paths by reducing the number of points using RDP algorithm.
    """
    simplified_paths = []
    for path in paths:
        points = []
        for segment in path:
            points.append(segment.start)
            points.append(segment.end)
        unique_points = []
        for pt in points:
            if not unique_points or (pt.real != unique_points[-1].real or pt.imag != unique_points[-1].imag):
                unique_points.append(pt)
        simplified_points = rdp(unique_points, tolerance)
        simplified_path = SvgPath()
        for i in range(len(simplified_points)-1):
            simplified_path.append(Line(simplified_points[i], simplified_points[i+1]))
        simplified_paths.append(simplified_path)
    return simplified_paths



def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
    """
    Convert SVG paths to embroidery stitches based on user-defined settings.
    
    Args:
        svg_path (Path): Path to the SVG file.
        settings (Dict): Dictionary containing settings like stitch_density and stitch_type.
    
    Returns:
        EmbPattern: The generated embroidery pattern.
    """
    try:
        # Parse SVG paths
        paths, attributes = svg2paths(str(svg_path))
        logging.debug(f"Parsed {len(paths)} paths from {svg_path}")

        # Simplify paths based on stitch density
        tolerance = settings.get("stitch_density", 2.0)
        simplified_paths = simplify_paths(paths, tolerance=tolerance)
        logging.debug(f"Simplified paths with tolerance {tolerance}")

        # Create a new embroidery pattern
        pattern = EmbPattern()

        # Convert SVG paths to embroidery stitches
        for path in simplified_paths:
            for segment in path:
                start = segment.start
                end = segment.end
                stitch_type = settings.get("stitch_type", "normal")

                if stitch_type == "jump":
                    # Use JUMP command for non-stitch movements
                    pattern.add_stitch_absolute(JUMP, end.real, end.imag)
                else:
                    # Use STITCH command for regular stitching
                    pattern.add_stitch_absolute(STITCH, end.real, end.imag)

        # Mark the end of the pattern
        pattern.add_command(END)  # Correct command to end the pattern

        logging.info(f"Stitches successfully generated from {svg_path}")
        return pattern
    except Exception as e:
        logging.error(f"Error in generate_stitches: {e}")
        raise e


def save_dst(pattern: EmbPattern, output_filename: str) -> Path:
    """
    Save the embroidery pattern to a DST file.
    """
    try:
        dst_path = OUTPUT_DIR / output_filename
        write_dst(pattern, str(dst_path))
        logging.info(f"DST file saved to {dst_path}")
        return dst_path
    except Exception as e:
        logging.error(f"Error in save_dst: {e}")
        raise e

async def digitize_image(client_id: str, image_path: Path, settings: Dict):
    """
    Full digitization pipeline: preprocess, vectorize, generate stitches, and save DST.
    Sends updates to the client via WebSocket.
    """
    try:
        await manager.send_message(client_id, "Preprocessing image...")
        processed_image = await preprocess_image(image_path)

        await manager.send_message(client_id, "Vectorizing image...")
        svg_image = vectorize_image(processed_image)

        await manager.send_message(client_id, "Generating stitches...")
        pattern = generate_stitches(svg_image, settings)

        await manager.send_message(client_id, "Saving DST file...")
        output_filename = image_path.stem + ".dst"
        dst_file = save_dst(pattern, output_filename)

        await manager.send_message(client_id, "Digitization complete.")

    except Exception as e:
        await manager.send_message(client_id, f"Error during digitization: {str(e)}")
        logging.error(f"Error in digitize_image: {e}")

# ---------------------
# API Endpoints
# ---------------------

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


@app.get("/preview/{filename}", response_class=FileResponse)
async def preview_file(filename: str):
    """
    Endpoint to fetch the SVG representation of the uploaded file.
    """
    # Ensure directories exist
    ensure_directories()

    # Look for the processed SVG file in PROCESSED_DIR
    svg_file_path = PROCESSED_DIR / f"{filename}_processed.svg"

    # Check if the SVG file exists
    if not svg_file_path.exists():
        logging.error(f"SVG file not found: {svg_file_path}")
        raise HTTPException(status_code=404, detail="SVG file not found.")

    try:
        return FileResponse(
            path=str(svg_file_path),
            media_type='image/svg+xml',
            filename=f"{filename}.svg"
        )
    except Exception as e:
        logging.error(f"Error serving SVG file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error serving SVG file")


# ---------------------
# WebSocket Endpoint
# ---------------------

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)