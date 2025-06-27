#!/usr/bin/env python3
"""
Automotive Measurement Analysis Backend Server
FastAPI server for processing MDF/BLF files and providing data access
"""

import os
import sys
import logging
from pathlib import Path

# Add local packages directory to Python path if it exists
current_dir = Path(__file__).parent
python_packages_dir = current_dir / "python_packages"
if python_packages_dir.exists():
    sys.path.insert(0, str(python_packages_dir))
    logging.info(f"Added {python_packages_dir} to Python path")

# Also add the current directory to path for relative imports
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from typing import List, Optional, Dict, Any

try:
    import uvicorn
except ImportError as e:
    logging.error(f"Failed to import uvicorn: {e}")
    logging.error("Please install required dependencies:")
    logging.error("pip install -r requirements.txt")
    sys.exit(1)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from parsers.mdf_parser import MDFParser
from parsers.blf_parser import BLFParser
from models.data_models import FileInfo, SignalInfo, SignalData
from utils.chunking import DataChunker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Automotive Analysis Backend",
    description="Backend service for automotive measurement data analysis",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to VS Code extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers
mdf_parser = MDFParser()
blf_parser = BLFParser()
data_chunker = DataChunker()

# Request/Response models
class FileInfoRequest(BaseModel):
    file_path: str = Field(..., description="Path to the measurement file")

class SignalsRequest(BaseModel):
    file_path: str = Field(..., description="Path to the measurement file")

class DataRequest(BaseModel):
    file_path: str = Field(..., description="Path to the measurement file")
    signals: List[str] = Field(..., description="List of signal names to retrieve")
    start_time: Optional[float] = Field(None, description="Start time in seconds")
    end_time: Optional[float] = Field(None, description="End time in seconds")

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    parsers: Dict[str, bool]

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        parsers={
            "mdf": mdf_parser.is_available(),
            "blf": blf_parser.is_available()
        }
    )

@app.post("/files/info")
async def get_file_info(request: FileInfoRequest) -> FileInfo:
    """Get file metadata and information"""
    try:
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine file type and use appropriate parser
        file_extension = file_path.suffix.lower()
        
        if file_extension in ['.mdf', '.mf4']:
            file_info = await mdf_parser.get_file_info(file_path)
        elif file_extension in ['.blf', '.asc']:
            file_info = await blf_parser.get_file_info(file_path)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}"
            )
        
        logger.info(f"Retrieved file info for {file_path}")
        return file_info
        
    except Exception as e:
        logger.error(f"Error getting file info for {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals")
async def get_signals(request: SignalsRequest) -> Dict[str, Any]:
    """Get available signals from the file"""
    try:
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine file type and use appropriate parser
        file_extension = file_path.suffix.lower()
        
        if file_extension in ['.mdf', '.mf4']:
            signals = await mdf_parser.get_signals(file_path)
        elif file_extension in ['.blf', '.asc']:
            signals = await blf_parser.get_signals(file_path)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}"
            )
        
        logger.info(f"Retrieved {len(signals.channels)} signals from {file_path}")
        return signals.dict()
        
    except Exception as e:
        logger.error(f"Error getting signals for {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data")
async def get_signal_data(request: DataRequest) -> SignalData:
    """Get signal data for specified time range"""
    try:
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine file type and use appropriate parser
        file_extension = file_path.suffix.lower()
        
        if file_extension in ['.mdf', '.mf4']:
            signal_data = await mdf_parser.get_signal_data(
                file_path, 
                request.signals, 
                request.start_time, 
                request.end_time
            )
        elif file_extension in ['.blf', '.asc']:
            signal_data = await blf_parser.get_signal_data(
                file_path, 
                request.signals, 
                request.start_time, 
                request.end_time
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}"
            )
        
        logger.info(f"Retrieved data for {len(request.signals)} signals from {file_path}")
        return signal_data
        
    except Exception as e:
        logger.error(f"Error getting signal data for {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize parsers on startup"""
    logger.info("Starting Automotive Analysis Backend")
    
    # Check parser availability
    mdf_available = mdf_parser.is_available()
    blf_available = blf_parser.is_available()
    
    logger.info(f"MDF Parser available: {mdf_available}")
    logger.info(f"BLF Parser available: {blf_available}")
    
    if not mdf_available and not blf_available:
        logger.warning("No file parsers are available!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Automotive Analysis Backend")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info"
    ) 