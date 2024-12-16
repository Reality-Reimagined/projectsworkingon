# # backend/main.py

# import os
# import uuid
# import shutil
# import asyncio
# import logging
# import math
# from pathlib import Path
# from typing import Optional, Dict, Any, List

# import aiofiles
# import cv2
# import numpy as np
# from PIL import Image, ImageFilter

# # from pyembroidery import *
# import pyembroidery 
# from svgpathtools import svg2paths, Path as SvgPath, Line

# from fastapi import (
#     FastAPI, 
#     UploadFile, 
#     File, 
#     WebSocket, 
#     WebSocketDisconnect, 
#     BackgroundTasks, 
#     HTTPException, 
#     Request
# )
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.websockets import WebSocketState
# from pydantic import BaseModel, Field

# import magic  # Ensure python-magic is installed


# # ---------------------
# # Configuration and Path Setup
# # ---------------------

# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# PROCESSED_DIR = BASE_DIR / "processed"
# OUTPUT_DIR = BASE_DIR / "outputs"
# LOG_DIR = BASE_DIR / "logs"

# # Ensure directories exist
# for directory in [UPLOAD_DIR, PROCESSED_DIR, OUTPUT_DIR, LOG_DIR]:
#     directory.mkdir(parents=True, exist_ok=True)

# # ---------------------
# # Logging Configuration
# # ---------------------

# logging.basicConfig(
#     filename=LOG_DIR / "digitization.log",
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s: %(message)s'
# )
# logger = logging.getLogger(__name__)

# # ---------------------
# # WebSocket Connection Manager
# # ---------------------

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}
#         self.file_status: Dict[str, Dict[str, Any]] = {}

#     async def connect(self, client_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket
#         logger.info(f"WebSocket connected: {client_id}")

#     def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]
#         logger.info(f"WebSocket disconnected: {client_id}")

#     async def send_message(self, client_id: str, message: str):
#         websocket = self.active_connections.get(client_id)
#         if websocket and websocket.client_state != WebSocketState.DISCONNECTED:
#             try:
#                 await websocket.send_text(message)
#                 logger.info(f"Sent message to {client_id}: {message}")
#             except Exception as e:
#                 logger.error(f"Error sending message to {client_id}: {e}")

#     def update_file_status(self, client_id: str, filename: str, status: str):
#         if client_id not in self.file_status:
#             self.file_status[client_id] = {}
#         self.file_status[client_id][filename] = {
#             "status": status,
#             "timestamp": asyncio.get_event_loop().time()
#         }

# # Initialize Connection Manager
# manager = ConnectionManager()

# # ---------------------
# # Pydantic Models
# # ---------------------

# class DigitizationSettings(BaseModel):
#     stitch_density: int = Field(default=10, ge=1, le=100)
#     stitch_type: str = Field(default="normal")
#     color: Optional[str] = None  # Optional: For multi-color support

# class FileProcessResponse(BaseModel):
#     filename: str
#     status: str
#     download_url: Optional[str] = None

# # ---------------------
# # Utility Functions
# # ---------------------

# def get_unique_filename(filename: str) -> str:
#     """Generate a unique filename to prevent overwriting."""
#     unique_id = uuid.uuid4().hex
#     base, ext = os.path.splitext(filename)
#     return f"{base}_{unique_id}{ext}"

# def validate_file_type(file_path: Path) -> bool:
#     """Validate file type using python-magic."""
#     try:
#         mime = magic.Magic(mime=True)
#         file_type = mime.from_file(str(file_path))
#         return file_type in ['image/png', 'image/jpeg', 'image/jpg']
#     except Exception as e:
#         logger.error(f"File type validation error: {e}")
#         return False

# async def save_upload_file(upload_file: UploadFile, destination: Path):
#     """Save uploaded file to the destination."""
#     try:
#         async with aiofiles.open(destination, 'wb') as out_file:
#             while True:
#                 content = await upload_file.read(1024)  # Read in chunks
#                 if not content:
#                     break
#                 await out_file.write(content)
#         logger.info(f"File saved to {destination}")
#     except Exception as e:
#         logger.error(f"Error saving file {destination}: {e}")
#         raise

# # ---------------------
# # Digitization Functions
# # ---------------------

# def perpendicular_distance(point, start, end):
#     """
#     Calculate the perpendicular distance from a point to a line segment.
#     """
#     if start == end:
#         return math.hypot(point.real - start.real, point.imag - start.imag)
#     else:
#         n = abs((end.real - start.real) * (start.imag - point.imag) - 
#                 (start.real - point.real) * (end.imag - start.imag))
#         d = math.hypot(end.real - start.real, end.imag - start.imag)
#         return n / d

# def rdp(points: List[complex], epsilon: float) -> List[complex]:
#     """
#     Ramer-Douglas-Peucker algorithm to simplify points.
#     """
#     # Find the point with the maximum distance
#     dmax = 0.0
#     index = 0
#     end = len(points) - 1

#     # Skip if not enough points
#     if end <= 1:
#         return points

#     for i in range(1, end):
#         d = perpendicular_distance(points[i], points[0], points[end])
#         if d > dmax:
#             index = i
#             dmax = d

#     # If max distance is greater than epsilon, recursively simplify
#     if dmax > epsilon:
#         # Recursive call
#         rec_results1 = rdp(points[:index+1], epsilon)
#         rec_results2 = rdp(points[index:], epsilon)
#         # Combine results
#         result = rec_results1[:-1] + rec_results2
#     else:
#         result = [points[0], points[end]]

#     return result

# def simplify_paths(paths: List[SvgPath], tolerance: float = 2.0) -> List[SvgPath]:
#     """
#     Simplify SVG paths by reducing the number of points using RDP algorithm.
#     """
#     simplified_paths = []
#     for path in paths:
#         # Extract points
#         points = []
#         for segment in path:
#             points.append(segment.start)
#             points.append(segment.end)

#         # Remove duplicates while preserving order
#         unique_points = []
#         for pt in points:
#             if not unique_points or (pt.real != unique_points[-1].real or pt.imag != unique_points[-1].imag):
#                 unique_points.append(pt)

#         # Apply RDP
#         simplified_points = rdp(unique_points, tolerance)

#         # Reconstruct simplified path
#         simplified_path = SvgPath()
#         for i in range(len(simplified_points)-1):
#             simplified_path.append(Line(simplified_points[i], simplified_points[i+1]))

#         simplified_paths.append(simplified_path)
#     return simplified_paths

# def generate_stitches(paths: List[SvgPath], settings: Dict[str, Any]) -> pyembroidery.EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         pattern = pyembroidery.EmbPattern()

#         for path in paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end

#                 # Assign stitch type based on settings or default
#                 stitch_type = settings.get("stitch_type", "normal")
#                 if stitch_type.lower() == "satin":
#                     stitch_enum = pyembroidery.STITCH_SATIN
#                 else:
#                     stitch_enum = pyembroidery.STITCH_NORMAL

#                 # Add stitches
#                 pattern.add_stitch_absolute(
#                     pyembroidery.EmbStitch(
#                         abs_x=start.real, 
#                         abs_y=start.imag, 
#                         stitch_type=stitch_enum
#                     )
#                 )
#                 pattern.add_stitch_absolute(
#                     pyembroidery.EmbStitch(
#                         abs_x=end.real, 
#                         abs_y=end.imag, 
#                         stitch_type=stitch_enum
#                     )
#                 )

#         # End of pattern marker
#         pattern.add_stitch_none()
#         logger.info("Stitches generated successfully.")
#         return pattern

#     except Exception as e:
#         logger.error(f"Error generating stitches: {e}")
#         raise

# def save_dst(pattern: pyembroidery.EmbPattern, output_filename: str) -> Path:
#     """
#     Save the embroidery pattern to a DST file.
#     """
#     try:
#         dst_path = OUTPUT_DIR / output_filename
#         pyembroidery.write_dst(pattern, str(dst_path))
#         logger.info(f"DST file saved to {dst_path}")
#         return dst_path

#     except Exception as e:
#         logger.error(f"Error saving DST: {e}")
#         raise

# async def digitize_image(
#     client_id: str, 
#     image_path: Path, 
#     settings: DigitizationSettings,
#     connection_manager: ConnectionManager
# ):
#     """
#     Full digitization pipeline: preprocess, vectorize, generate stitches, and save DST.
#     Sends updates to the client via WebSocket.
#     """
#     try:
#         await connection_manager.send_message(client_id, "Starting digitization...")

#         # Preprocessing
#         await connection_manager.send_message(client_id, "Preprocessing image...")
#         processed_image = await preprocess_image(image_path)

#         # Vectorization
#         await connection_manager.send_message(client_id, "Vectorizing image...")
#         svg_filename = f"{processed_image.stem}.svg"
#         svg_path = PROCESSED_DIR / svg_filename

#         # Call Potrace to convert BMP to SVG
#         try:
#             subprocess.run(
#                 ['potrace', str(processed_image), '-s', '-o', str(svg_path)],
#                 check=True
#             )
#             logger.info(f"Vector image saved to {svg_path}")
#             await connection_manager.send_message(client_id, "Vectorization complete.")
#         except subprocess.CalledProcessError as e:
#             logger.error(f"Potrace failed: {e}")
#             await connection_manager.send_message(client_id, "Vectorization failed.")
#             return

#         # Load and simplify paths
#         paths, _ = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.stitch_density)

#         # Generate stitches
#         await connection_manager.send_message(client_id, "Generating embroidery pattern...")
#         pattern = generate_stitches(simplified_paths, settings)

#         # Save DST
#         output_filename = f"{processed_image.stem}.dst"
#         await connection_manager.send_message(client_id, "Saving DST file...")
#         dst_file = save_dst(pattern, output_filename)

#         # Update file status
#         connection_manager.update_file_status(client_id, output_filename, "completed")

#         # Notify completion
#         download_url = f"/download/{output_filename}"
#         await connection_manager.send_message(client_id, f"Digitization complete. Download at {download_url}")

#     except Exception as e:
#         logger.error(f"Digitization error: {e}")
#         await connection_manager.send_message(client_id, f"Digitization failed: {str(e)}")
#         connection_manager.update_file_status(client_id, output_filename, "failed")

# # ---------------------
# # FastAPI App Initialization
# # ---------------------

# app = FastAPI(
#     title="Embroidery Digitization API",
#     description="Advanced image to embroidery file conversion service",
#     version="2.0.0"
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust as needed for security
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------
# # API Endpoints
# # ---------------------

# @app.post("/upload/", response_model=FileProcessResponse)
# async def upload_image(
#     background_tasks: BackgroundTasks,
#     request: Request,
#     file: UploadFile = File(...),
#     stitch_density: Optional[int] = Field(default=10, ge=1, le=100),
#     stitch_type: Optional[str] = Field(default="normal"),
#     client_id: Optional[str] = ""
# ):
#     """
#     Endpoint to upload an image and receive the embroidered DST file.
#     """
#     if not client_id:
#         raise HTTPException(status_code=400, detail="Client ID is required for WebSocket communication.")

#     # File validation
#     if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
#         raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

#     # Limit file size (e.g., 10 MB)
#     max_file_size = 10 * 1024 * 1024  # 10 MB
#     contents = await file.read()
#     if len(contents) > max_file_size:
#         raise HTTPException(status_code=413, detail="File too large. Max size is 10MB.")
#     await file.seek(0)  # Reset file pointer

#     # Generate a unique filename
#     unique_filename = get_unique_filename(file.filename)
#     upload_path = UPLOAD_DIR / unique_filename

#     # Save the uploaded file
#     try:
#         async with aiofiles.open(upload_path, 'wb') as out_file:
#             while True:
#                 chunk = await file.read(1024)  # Read in chunks
#                 if not chunk:
#                     break
#                 await out_file.write(chunk)
#         logger.info(f"File uploaded and saved to {upload_path}")
#     except Exception as e:
#         logger.error(f"Error saving uploaded file: {e}")
#         raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

#     # Validate file type using python-magic
#     if not validate_file_type(upload_path):
#         os.unlink(upload_path)  # Remove invalid file
#         logger.warning(f"Uploaded file has invalid type: {upload_path}")
#         raise HTTPException(status_code=400, detail="Invalid file type after validation.")

#     # Prepare digitization settings
#     settings = DigitizationSettings(
#         stitch_density=stitch_density,
#         stitch_type=stitch_type
#     )

#     # Start digitization in the background
#     background_tasks.add_task(
#         digitize_image, 
#         client_id, 
#         upload_path, 
#         settings, 
#         manager
#     )

#     # Generate download URL (will be available after processing)
#     download_url = f"/download/{unique_filename.split('.')[0]}.dst"

#     return FileProcessResponse(
#         filename=unique_filename.split('.')[0] + ".dst",
#         status="processing",
#         download_url=download_url
#     )

# @app.get("/download/{filename}", response_class=FileResponse)
# async def download_file(filename: str, client_id: Optional[str] = ""):
#     """
#     Endpoint to download the generated DST file.
#     """
#     file_path = OUTPUT_DIR / filename
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found.")

#     return FileResponse(
#         path=str(file_path),
#         filename=filename,
#         media_type='application/octet-stream'
#     )

# # ---------------------
# # WebSocket Endpoint
# # ---------------------

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(client_id, websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # Echo received message or handle accordingly
#             await websocket.send_text(f"Message received: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(client_id)
#     except Exception as e:
#         logger.error(f"WebSocket error with client {client_id}: {e}")
#         manager.disconnect(client_id)

# # ---------------------
# # Status Endpoint (Optional)
# # ---------------------

# @app.get("/status/{filename}")
# async def get_file_status(filename: str, client_id: str = ""):
#     """
#     Endpoint to get the processing status of a file.
#     """
#     status = manager.file_status.get(client_id, {}).get(filename)
#     if not status:
#         return JSONResponse(
#             status_code=404, 
#             content={"detail": "No status found for this file"}
#         )
#     return status

# # ---------------------
# # Image Preview Generation (Optional)
# # ---------------------

# def generate_preview(image_path: Path, dst_path: Path) -> Path:
#     """
#     Generate a preview image of the embroidery design.
#     This can be a simplified version of the vectorized design.
#     """
#     try:
#         # Load the DST file and extract stitch data
#         pattern = pyembroidery.read_dst(str(dst_path))
#         stitches = pattern.stitches

#         # Create an image canvas
#         image = Image.new('RGB', (800, 800), color='white')
#         draw = Image.Draw.Draw(image)

#         # Draw stitches
#         prev_stitch = None
#         for stitch in stitches:
#             if stitch.stitch_type == pyembroidery.STITCH_STOP:
#                 prev_stitch = None
#                 continue
#             current_stitch = (int(stitch.abs_x), int(stitch.abs_y))
#             if prev_stitch:
#                 draw.line([prev_stitch, current_stitch], fill='black', width=1)
#             prev_stitch = current_stitch

#         preview_filename = f"{dst_path.stem}_preview.png"
#         preview_path = PROCESSED_DIR / preview_filename
#         image.save(preview_path)
#         logger.info(f"Preview image saved to {preview_path}")
#         return preview_path

#     except Exception as e:
#         logger.error(f"Error generating preview: {e}")
#         raise

# # # ---------------------
# # # Import Statements for Preview
# # # ---------------------

# import os
# import uuid
# import shutil
# import subprocess
# from pathlib import Path
# from typing import Optional, Dict

# from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from pydantic import BaseModel

# from pyembroidery import EmbPattern, STITCH, JUMP, END, write_dst
# from svgpathtools import svg2paths, Path as SvgPath, Line
# from PIL import Image, ImageFilter
# import cv2
# import numpy as np
# import logging
# import asyncio
# import math

# # ---------------------
# # Configuration
# # ---------------------

# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# PROCESSED_DIR = BASE_DIR / "processed"
# OUTPUT_DIR = BASE_DIR / "outputs"
# LOG_DIR = BASE_DIR / "logs"
# DOWNLOAD_DIR = BASE_DIR / "download"

# # Create directories if they don't exist and ensure proper permissions
# def ensure_directories():
#     directories = [UPLOAD_DIR, PROCESSED_DIR, OUTPUT_DIR, LOG_DIR, DOWNLOAD_DIR]
#     for directory in directories:
#         directory.mkdir(parents=True, exist_ok=True)
#         # Ensure directory has proper permissions (755)
#         try:
#             directory.chmod(0o755)
#         except Exception as e:
#             logging.warning(f"Could not set permissions for {directory}: {e}")

# # Initialize directories
# ensure_directories()

# # Logging configuration
# logging.basicConfig(
#     filename=LOG_DIR / "digitization.log",
#     level=logging.INFO,
#     format='%(asctime)s:%(levelname)s:%(message)s'
# )

# # ---------------------
# # FastAPI App Initialization
# # ---------------------

# app = FastAPI(
#     title="Embroidery Digitization API",
#     description="API for converting images to embroidery files (DST)",
#     version="1.0.0"
# )

# # Allow CORS for frontend interaction
# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "*",  # React default port
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------
# # WebSocket Manager
# # ---------------------

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}  # client_id: WebSocket

#     async def connect(self, client_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket
#         logging.info(f"WebSocket connected: {client_id}")

#     def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]
#             logging.info(f"WebSocket disconnected: {client_id}")

#     async def send_message(self, client_id: str, message: str):
#         if client_id in self.active_connections:
#             websocket = self.active_connections[client_id]
#             await websocket.send_text(message)
#             logging.info(f"Sent message to {client_id}: {message}")

# manager = ConnectionManager()

# # ---------------------
# # Pydantic Schemas
# # ---------------------

# class UploadResponse(BaseModel):
#     filename: str
#     download_url: str
#     message: Optional[str] = "Embroidery file created successfully."

# class DigitizationSettings(BaseModel):
#     stitch_density: Optional[float] = 2.0  # Example setting as float
#     stitch_type: Optional[str] = "normal"  # "normal" or "jump"

# # ---------------------
# # Utility Functions
# # ---------------------

# def get_unique_filename(filename: str) -> str:
#     """Generate a unique filename to prevent overwriting."""
#     unique_id = uuid.uuid4().hex
#     base, ext = os.path.splitext(filename)
#     return f"{base}_{unique_id}{ext}"

# # ---------------------
# # Digitization Functions
# # ---------------------

# def perpendicular_distance(point, start, end):
#     """
#     Calculate the perpendicular distance from a point to a line segment.
#     """
#     if start == end:
#         return math.hypot(point.real - start.real, point.imag - start.imag)
#     else:
#         n = abs((end.real - start.real) * (start.imag - point.imag) - 
#                 (start.real - point.real) * (end.imag - start.imag))
#         d = math.hypot(end.real - start.real, end.imag - start.imag)
#         return n / d

# def rdp(points, epsilon):
#     """
#     Ramer-Douglas-Peucker algorithm to simplify points.
#     """
#     dmax = 0.0
#     index = 0
#     end = len(points) - 1
#     for i in range(1, end):
#         d = perpendicular_distance(points[i], points[0], points[end])
#         if d > dmax:
#             index = i
#             dmax = d
#     if dmax > epsilon:
#         rec_results1 = rdp(points[:index+1], epsilon)
#         rec_results2 = rdp(points[index:], epsilon)
#         result = rec_results1[:-1] + rec_results2
#     else:
#         result = [points[0], points[end]]
#     return result

# def simplify_paths(paths, tolerance=2.0):
#     """
#     Simplify SVG paths by reducing the number of points using RDP algorithm.
#     """
#     simplified_paths = []
#     for path in paths:
#         points = []
#         for segment in path:
#             points.append(segment.start)
#             points.append(segment.end)
#         unique_points = []
#         for pt in points:
#             if not unique_points or (pt.real != unique_points[-1].real or pt.imag != unique_points[-1].imag):
#                 unique_points.append(pt)
#         simplified_points = rdp(unique_points, tolerance)
#         simplified_path = SvgPath()
#         for i in range(len(simplified_points)-1):
#             simplified_path.append(Line(simplified_points[i], simplified_points[i+1]))
#         simplified_paths.append(simplified_path)
#     return simplified_paths

# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
    
#     Args:
#         svg_path (Path): Path to the SVG file.
#         settings (Dict): Dictionary containing settings like stitch_density and stitch_type.
    
#     Returns:
#         EmbPattern: The generated embroidery pattern.
#     """
#     try:
#         # Parse SVG paths
#         paths, attributes = svg2paths(str(svg_path))
#         logging.debug(f"Parsed {len(paths)} paths from {svg_path}")

#         # Simplify paths based on stitch density
#         tolerance = settings.get("stitch_density", 2.0)
#         simplified_paths = simplify_paths(paths, tolerance=tolerance)
#         logging.debug(f"Simplified paths with tolerance {tolerance}")

#         # Create a new embroidery pattern
#         pattern = EmbPattern()

#         total_stitches = 0
#         MAX_STITCHES = 10000  # Example limit; adjust as needed

#         # Convert SVG paths to embroidery stitches
#         for path_idx, path in enumerate(simplified_paths):
#             logging.debug(f"Processing path {path_idx + 1}/{len(simplified_paths)}")
#             points = []

#             # Extract unique end points from the simplified path
#             for segment in path:
#                 points.append(segment.end)

#             if not points:
#                 continue  # Skip empty paths

#             # Initialize with a JUMP to the first point to start stitching
#             first_point = points[0]
#             pattern.add_stitch_absolute(JUMP, first_point.real, first_point.imag)
#             logging.debug(f"Added JUMP to ({first_point.real}, {first_point.imag})")
#             total_stitches += 1

#             # Add STITCH or JUMP commands for subsequent points
#             for point in points[1:]:
#                 stitch_type = settings.get("stitch_type", "normal")
#                 if stitch_type.lower() == "jump":
#                     # Use JUMP command for non-stitch movements
#                     pattern.add_stitch_absolute(JUMP, point.real, point.imag)
#                     logging.debug(f"Added JUMP to ({point.real}, {point.imag})")
#                 else:
#                     # Use STITCH command for regular stitching
#                     pattern.add_stitch_absolute(STITCH, point.real, point.imag)
#                     logging.debug(f"Added STITCH to ({point.real}, {point.imag})")

#                 total_stitches += 1
#                 if total_stitches > MAX_STITCHES:
#                     raise ValueError("Generated stitch count exceeds the maximum allowed limit.")

#         # Mark the end of the pattern
#         pattern.add_command(END)  # Correct command to end the pattern
#         logging.info(f"Stitches successfully generated from {svg_path}")
#         logging.info(f"Total stitches in pattern: {total_stitches}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}", exc_info=True)
#         raise e

# def save_dst(pattern: EmbPattern, output_filename: str) -> Path:
#     """
#     Save the embroidery pattern to a DST file.
#     """
#     try:
#         dst_path = OUTPUT_DIR / output_filename
#         write_dst(pattern, str(dst_path))
#         file_size = dst_path.stat().st_size
#         logging.info(f"DST file saved to {dst_path} (Size: {file_size} bytes)")
#         return dst_path
#     except Exception as e:
#         logging.error(f"Error in save_dst: {e}")
#         raise e

# async def digitize_image(client_id: str, image_path: Path, settings: Dict):
#     """
#     Full digitization pipeline: preprocess, vectorize, generate stitches, and save DST.
#     Sends updates to the client via WebSocket.
#     """
#     try:
#         await manager.send_message(client_id, "Preprocessing image...")
#         processed_image = await preprocess_image(image_path)

#         await manager.send_message(client_id, "Vectorizing image...")
#         svg_image = vectorize_image(processed_image)

#         await manager.send_message(client_id, "Generating stitches...")
#         pattern = generate_stitches(svg_image, settings)

#         await manager.send_message(client_id, "Saving DST file...")
#         output_filename = f"{Path(image_path.stem).stem}.dst"  # Ensure correct naming
#         dst_file = save_dst(pattern, output_filename)

#         await manager.send_message(client_id, "Digitization complete.")

#     except Exception as e:
#         await manager.send_message(client_id, f"Error during digitization: {str(e)}")
#         logging.error(f"Error in digitize_image: {e}", exc_info=True)

# # ---------------------
# # API Endpoints
# # ---------------------

# @app.post("/upload/", response_model=UploadResponse)
# async def upload_image(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     client_id: str = Form(...),
#     stitch_density: float = Form(default=2.0),
#     stitch_type: str = Form(default="normal")
# ):
#     """
#     Endpoint to upload an image and receive the embroidered DST file.
#     """
#     # Ensure directories exist
#     ensure_directories()
    
#     logging.info(f"Received upload request - client_id: {client_id}, stitch_density: {stitch_density}, stitch_type: {stitch_type}")

#     try:
#         # Validate file type
#         if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
#             raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

#         # Limit file size (10 MB)
#         max_file_size = 10 * 1024 * 1024
#         contents = await file.read()
#         if len(contents) > max_file_size:
#             raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
#         await file.seek(0)

#         # Generate unique filename and save file
#         unique_filename = get_unique_filename(file.filename)
#         upload_path = UPLOAD_DIR / unique_filename
        
#         with open(upload_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Prepare settings
#         settings = {
#             "stitch_density": stitch_density,
#             "stitch_type": stitch_type
#         }

#         logging.info(f"File saved to {upload_path}, starting digitization with settings: {settings}")

#         # Start digitization in background
#         background_tasks.add_task(digitize_image, client_id, upload_path, settings)

#         # Generate download URL
#         dst_filename = f"{Path(unique_filename).stem}.dst"
#         download_url = f"/download/{dst_filename}"

#         return UploadResponse(
#             filename=dst_filename,
#             download_url=download_url,
#             message="Embroidery file is being created. Check updates via WebSocket."
#         )

#     except HTTPException as he:
#         logging.error(f"HTTPException in upload_image: {he.detail}")
#         raise he
#     except Exception as e:
#         logging.error(f"Error in upload_image: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/download/{filename}", response_class=FileResponse)
# async def download_file(filename: str):
#     """
#     Endpoint to download the generated DST file.
#     """
#     # Ensure directories exist
#     ensure_directories()
    
#     file_path = OUTPUT_DIR / filename
#     if not file_path.exists():
#         logging.error(f"File not found: {file_path}")
#         raise HTTPException(status_code=404, detail="File not found.")
    
#     try:
#         return FileResponse(
#             path=str(file_path),
#             media_type='application/octet-stream',
#             filename=filename,
#             background=True  # Serve in background to prevent blocking
#         )
#     except Exception as e:
#         logging.error(f"Error serving file {filename}: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Error serving file")

# # ---------------------
# # WebSocket Endpoint
# # ---------------------

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(client_id, websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_message(client_id, f"Message received: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(client_id)





# from PIL import ImageDraw
## this one works very well. right up to the download button getting pressed. trying something 
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

# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         paths, attributes = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.get("stitch_density", 2.0))

#         pattern = EmbPattern()
#         for path in simplified_paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end
#                 stitch_type = settings.get("stitch_type", "normal")
#                 pattern.add_stitch_absolute(EmbStitch(abs_x=start.real, abs_y=start.imag, stitch_type=stitch_type))
#                 pattern.add_stitch_absolute(EmbStitch(abs_x=end.real, abs_y=end.imag, stitch_type=stitch_type))
#         pattern.add_stitch_none()  # End of pattern
#         logging.info(f"Stitches generated from {svg_path}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}")
#         raise e

# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         paths, attributes = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.get("stitch_density", 2.0))

#         pattern = EmbPattern()
#         for path in simplified_paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end
#                 stitch_type = settings.get("stitch_type", "normal")
#                 # Use correct method from pyembroidery
#                 pattern.add_stitch_absolute(start.real, start.imag)
#                 pattern.add_stitch_absolute(end.real, end.imag)

#         # pattern.add_stitch_none()  # End of pattern
#         pattern.add_command(COMMAND_END)  # End of pattern
#         logging.info(f"Stitches generated from {svg_path}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}")
#         raise e

# from pyembroidery import EmbPattern # Explicitly import EmbCommand
# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         paths, attributes = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.get("stitch_density", 2.0))

#         pattern = EmbPattern()
#         for path in simplified_paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end
#                 stitch_type = settings.get("stitch_type", "normal")
#                 # Use correct method from pyembroidery
#                 pattern.add_stitch_absolute(start.real, start.imag)
#                 pattern.add_stitch_absolute(end.real, end.imag)

#         pattern.add_stitch_none()  # End of pattern

#         logging.info(f"Stitches generated from {svg_path}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}")
#         raise e

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
# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         paths, attributes = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.get("stitch_density", 2.0))

#         pattern = EmbPattern()
#         for path in simplified_paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end
#                 stitch_type = settings.get("stitch_type", "normal")
#                 # Use correct method from pyembroidery
#                 pattern.add_stitch_absolute(start.real, start.imag)
#                 pattern.add_stitch_absolute(end.real, end.imag)

#         pattern.add_command(EmbCommand.END)  # End of pattern

#         logging.info(f"Stitches generated from {svg_path}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}")
#         raise e

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

# @app.post("/upload/", response_model=UploadResponse)
# async def upload_image(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     client_id: str = Form(...),
#     stitch_density: int = Form(default=2),
#     stitch_type: str = Form(default="normal")
# ):
#     """
#     Endpoint to upload an image and receive the embroidered DST file.
#     """
#     logging.info(f"Received upload request - client_id: {client_id}, stitch_density: {stitch_density}, stitch_type: {stitch_type}")

#     try:
#         # Validate file type
#         if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
#             raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

#         # Limit file size (10 MB)
#         max_file_size = 10 * 1024 * 1024
#         contents = await file.read()
#         if len(contents) > max_file_size:
#             raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
#         await file.seek(0)

#         # Generate unique filename and save file
#         unique_filename = get_unique_filename(file.filename)
#         upload_path = UPLOAD_DIR / unique_filename
        
#         with open(upload_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Prepare settings
#         settings = {
#             "stitch_density": stitch_density,
#             "stitch_type": stitch_type
#         }

#         logging.info(f"File saved to {upload_path}, starting digitization with settings: {settings}")

#         # Start digitization in background
#         background_tasks.add_task(digitize_image, client_id, upload_path, settings)

#         # Generate download URL
#         download_url = f"/download/{unique_filename.split('.')[0]}.dst"

#         return UploadResponse(
#             filename=unique_filename.split('.')[0] + ".dst",
#             download_url=download_url,
#             message="Embroidery file is being created. Check updates via WebSocket."
#         )

#     except Exception as e:
#         logging.error(f"Error in upload_image: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/download/{filename}", response_class=FileResponse)
# async def download_file(filename: str):
#     """
#     Endpoint to download the generated DST file.
#     """
#     file_path = OUTPUT_DIR / filename
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found.")
    
#     return FileResponse(
#         path=str(file_path),
#         media_type='application/octet-stream',
#         filename=filename
#     )

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



# # backend/main.py - deploys well

# import os
# import uuid
# import shutil
# import subprocess
# from pathlib import Path
# from typing import Optional, Dict

# from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Form
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from pydantic import BaseModel

# # from pyembroidery import EmbPattern, EmbStitch, write_dst
# from pyembroidery import *
# from svgpathtools import svg2paths, Path as SvgPath, Line
# from PIL import Image, ImageFilter
# import cv2
# import numpy as np
# import logging
# import asyncio

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

# # ---------------------
# # FastAPI App Initialization
# # ---------------------

# app = FastAPI(
#     title="Embroidery Digitization API",
#     description="API for converting images to embroidery files (DST)",
#     version="1.0.0"
# )

# # Allow CORS for frontend interaction
# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "*", # React default port
#     # Add other origins as needed
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------
# # WebSocket Manager
# # ---------------------

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}  # client_id: WebSocket

#     async def connect(self, client_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket
#         logging.info(f"WebSocket connected: {client_id}")

#     def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]
#             logging.info(f"WebSocket disconnected: {client_id}")

#     async def send_message(self, client_id: str, message: str):
#         if client_id in self.active_connections:
#             websocket = self.active_connections[client_id]
#             await websocket.send_text(message)
#             logging.info(f"Sent message to {client_id}: {message}")

# manager = ConnectionManager()

# # ---------------------
# # Pydantic Schemas
# # ---------------------

# class UploadResponse(BaseModel):
#     filename: str
#     download_url: str
#     message: Optional[str] = "Embroidery file created successfully."

# class DigitizationSettings(BaseModel):
#     stitch_density: Optional[int] = 10  # Example setting

# # ---------------------
# # Utility Functions
# # ---------------------

# def get_unique_filename(filename: str) -> str:
#     """Generate a unique filename to prevent overwriting."""
#     unique_id = uuid.uuid4().hex
#     base, ext = os.path.splitext(filename)
#     return f"{base}_{unique_id}{ext}"

# async def save_upload_file(upload_file: UploadFile, destination: Path):
#     """Save uploaded file to the destination."""
#     async with aiofiles.open(destination, 'wb') as out_file:
#         content = await upload_file.read()  # async read
#         await out_file.write(content)  # async write

# # ---------------------
# # Digitization Functions
# # ---------------------

# async def preprocess_image(image_path: Path) -> Path:
#     """
#     Preprocess the image: convert to grayscale, resize, and apply thresholding.
#     Save the processed image as a BMP file for Potrace.
#     """
#     try:
#         image = Image.open(image_path).convert('L')  # Convert to grayscale
#         image = image.resize((500, 500))  # Resize as needed
#         image = image.filter(ImageFilter.GaussianBlur(radius=1))  # Noise reduction
#         image_np = np.array(image)

#         # Apply adaptive thresholding for better results
#         thresh = cv2.adaptiveThreshold(
#             image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#             cv2.THRESH_BINARY, 11, 2
#         )

#         processed_filename = image_path.stem + "_processed.bmp"
#         processed_path = PROCESSED_DIR / processed_filename
#         cv2.imwrite(str(processed_path), thresh)
#         logging.info(f"Image preprocessed and saved to {processed_path}")
#         return processed_path
#     except Exception as e:
#         logging.error(f"Error in preprocess_image: {e}")
#         raise e

# def vectorize_image(processed_image_path: Path) -> Path:
#     """
#     Vectorize the processed bitmap image using Potrace via command line.
#     Save the output as an SVG file.
#     """
#     try:
#         svg_filename = processed_image_path.stem + ".svg"
#         svg_path = PROCESSED_DIR / svg_filename

#         # Call Potrace to convert BMP to SVG
#         subprocess.run(
#             ['potrace', str(processed_image_path), '-s', '-o', str(svg_path)],
#             check=True
#         )
#         logging.info(f"Vector image saved to {svg_path}")
#         return svg_path
#     except subprocess.CalledProcessError as e:
#         logging.error(f"Potrace failed: {e}")
#         raise e
#     except Exception as e:
#         logging.error(f"Error in vectorize_image: {e}")
#         raise e

# def perpendicular_distance(point, start, end):
#     """
#     Calculate the perpendicular distance from a point to a line segment.
#     """
#     if start == end:
#         return math.hypot(point.real - start.real, point.imag - start.imag)
#     else:
#         n = abs((end.real - start.real) * (start.imag - point.imag) - 
#                 (start.real - point.real) * (end.imag - start.imag))
#         d = math.hypot(end.real - start.real, end.imag - start.imag)
#         return n / d

# def rdp(points, epsilon):
#     """
#     Ramer-Douglas-Peucker algorithm to simplify points.
#     """
#     # Find the point with the maximum distance
#     dmax = 0.0
#     index = 0
#     end = len(points) - 1
#     for i in range(1, end):
#         d = perpendicular_distance(points[i], points[0], points[end])
#         if d > dmax:
#             index = i
#             dmax = d
#     # If max distance is greater than epsilon, recursively simplify
#     if dmax > epsilon:
#         # Recursive call
#         rec_results1 = rdp(points[:index+1], epsilon)
#         rec_results2 = rdp(points[index:], epsilon)
#         # Combine results
#         result = rec_results1[:-1] + rec_results2
#     else:
#         result = [points[0], points[end]]
#     return result

# def simplify_paths(paths, tolerance=2.0):
#     """
#     Simplify SVG paths by reducing the number of points using RDP algorithm.
#     """
#     simplified_paths = []
#     for path in paths:
#         points = []
#         for segment in path:
#             points.append(segment.start)
#             points.append(segment.end)
#         # Remove duplicates
#         unique_points = []
#         for pt in points:
#             if not unique_points or (pt.real != unique_points[-1].real or pt.imag != unique_points[-1].imag):
#                 unique_points.append(pt)
#         # Apply RDP
#         simplified_points = rdp(unique_points, tolerance)
#         # Reconstruct simplified path
#         simplified_path = SvgPath()
#         for i in range(len(simplified_points)-1):
#             simplified_path.append(Line(simplified_points[i], simplified_points[i+1]))
#         simplified_paths.append(simplified_path)
#     return simplified_paths

# def generate_stitches(svg_path: Path, settings: Dict) -> EmbPattern:
#     """
#     Convert SVG paths to embroidery stitches based on user-defined settings.
#     """
#     try:
#         paths, attributes = svg2paths(str(svg_path))
#         simplified_paths = simplify_paths(paths, tolerance=settings.get("stitch_density", 2.0))

#         pattern = EmbPattern()
#         for path in simplified_paths:
#             for segment in path:
#                 start = segment.start
#                 end = segment.end
#                 # Assign stitch type based on settings or default
#                 stitch_type = settings.get("stitch_type", "normal")
#                 pattern.add_stitch_absolute(EmbStitch(abs_x=start.real, abs_y=start.imag, stitch_type=stitch_type))
#                 pattern.add_stitch_absolute(EmbStitch(abs_x=end.real, abs_y=end.imag, stitch_type=stitch_type))
#         pattern.add_stitch_none()  # End of pattern
#         logging.info(f"Stitches generated from {svg_path}")
#         return pattern
#     except Exception as e:
#         logging.error(f"Error in generate_stitches: {e}")
#         raise e

# def save_dst(pattern: EmbPattern, output_filename: str) -> Path:
#     """
#     Save the embroidery pattern to a DST file.
#     """
#     try:
#         dst_path = OUTPUT_DIR / output_filename
#         write_dst(pattern, str(dst_path))
#         logging.info(f"DST file saved to {dst_path}")
#         return dst_path
#     except Exception as e:
#         logging.error(f"Error in save_dst: {e}")
#         raise e

# async def digitize_image(client_id: str, image_path: Path, settings: Dict):
#     """
#     Full digitization pipeline: preprocess, vectorize, generate stitches, and save DST.
#     Sends updates to the client via WebSocket.
#     """
#     try:
#         await manager.send_message(client_id, "Preprocessing image...")
#         processed_image = await preprocess_image(image_path)

#         await manager.send_message(client_id, "Vectorizing image...")
#         svg_image = vectorize_image(processed_image)

#         await manager.send_message(client_id, "Generating stitches...")
#         pattern = generate_stitches(svg_image, settings)

#         await manager.send_message(client_id, "Saving DST file...")
#         output_filename = image_path.stem + ".dst"
#         dst_file = save_dst(pattern, output_filename)

#         await manager.send_message(client_id, "Digitization complete.")

#     except Exception as e:
#         await manager.send_message(client_id, f"Error during digitization: {str(e)}")
#         logging.error(f"Error in digitize_image: {e}")

# ---------------------
# API Endpoints
# ---------------------

# @app.post("/upload/", response_model=UploadResponse)
# async def upload_image(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     stitch_density: Optional[int] = 2,
#     stitch_type: Optional[str] = "normal",
#     client_id: Optional[str] = None
# ):
#     """
#     Endpoint to upload an image and receive the embroidered DST file.
#     """
#     if client_id is None:
#         raise HTTPException(status_code=400, detail="Client ID is required for WebSocket communication.")

#     # Validate file type
#     if file.content_type not in ["image/png", "image/jpeg"]:
#         raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

#     # Limit file size (e.g., 10 MB)
#     max_file_size = 10 * 1024 * 1024  # 10 MB
#     contents = await file.read()
#     if len(contents) > max_file_size:
#         raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
#     await file.seek(0)  # Reset file pointer

#     # Generate a unique filename
#     unique_filename = get_unique_filename(file.filename)
#     upload_path = UPLOAD_DIR / unique_filename

#     # Save the uploaded file
#     with open(upload_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Prepare settings
#     settings = {
#         "stitch_density": stitch_density,
#         "stitch_type": stitch_type
#     }

#     # Start digitization in the background
#     background_tasks.add_task(digitize_image, client_id, upload_path, settings)

#     # Generate download URL
#     download_url = f"/download/{unique_filename.split('.')[0]}.dst"

#     return UploadResponse(
#         filename=unique_filename.split('.')[0] + ".dst",
#         download_url=download_url,
#         message="Embroidery file is being created. Check updates via WebSocket."
#     )

@app.post("/upload/", response_model=UploadResponse)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    stitch_density: Optional[int] = Form(2),
    stitch_type: Optional[str] = Form("normal"),
    client_id: Optional[str] = Form(None)
):
    """
    Endpoint to upload an image and receive the embroidered DST file.
    """
    # Log the received parameters
    logging.info(f"Received upload request - client_id: {client_id}, stitch_density: {stitch_density}, stitch_type: {stitch_type}")
    
    if client_id is None:
        raise HTTPException(status_code=400, detail="Client ID is required for WebSocket communication.")

    try:
        # Validate file type
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

        # Limit file size (e.g., 10 MB)
        max_file_size = 10 * 1024 * 1024  # 10 MB
        contents = await file.read()
        if len(contents) > max_file_size:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        await file.seek(0)  # Reset file pointer

        # Generate a unique filename
        unique_filename = get_unique_filename(file.filename)
        upload_path = UPLOAD_DIR / unique_filename

        # Save the uploaded file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Prepare settings
        settings = {
            "stitch_density": int(stitch_density),
            "stitch_type": stitch_type
        }

        logging.info(f"File saved to {upload_path}, starting digitization with settings: {settings}")

        # Start digitization in the background
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
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(
        path=str(file_path),
        media_type='application/octet-stream',
        filename=filename
    )

# ---------------------
# WebSocket Endpoint
# ---------------------

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Here, you can handle incoming messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
