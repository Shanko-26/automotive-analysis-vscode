"""
Data models for automotive measurement analysis
Pydantic models for API request/response validation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ChannelInfo(BaseModel):
    """Information about a measurement channel/signal"""
    name: str = Field(..., description="Signal name")
    unit: str = Field(..., description="Signal unit")
    sample_rate: float = Field(..., description="Sample rate in Hz")
    min_value: float = Field(..., description="Minimum value in the signal")
    max_value: float = Field(..., description="Maximum value in the signal")
    description: Optional[str] = Field(None, description="Signal description")
    source: Optional[str] = Field(None, description="Signal source/ECU")

class FileInfo(BaseModel):
    """File metadata and information"""
    file_path: str = Field(..., description="Path to the file")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type (MDF, BLF, etc.)")
    duration: float = Field(..., description="Recording duration in seconds")
    signal_count: int = Field(..., description="Number of signals in the file")
    recording_date: Optional[datetime] = Field(None, description="Recording date and time")
    measurement_system: Optional[str] = Field(None, description="Measurement system used")
    channels: List[ChannelInfo] = Field(default_factory=list, description="List of available channels")

class SignalInfo(BaseModel):
    """Information about available signals"""
    file_path: str = Field(..., description="Path to the file")
    channels: List[ChannelInfo] = Field(..., description="List of available channels")
    total_channels: int = Field(..., description="Total number of channels")

class SignalData(BaseModel):
    """Signal data for plotting and analysis"""
    file_path: str = Field(..., description="Path to the file")
    signals: List[str] = Field(..., description="List of signal names")
    timestamps: List[float] = Field(..., description="Time array in seconds")
    data: Dict[str, List[float]] = Field(..., description="Signal data by name")
    start_time: float = Field(..., description="Start time of the data")
    end_time: float = Field(..., description="End time of the data")
    sample_count: int = Field(..., description="Number of samples")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    parsers: Dict[str, bool] = Field(..., description="Parser availability status") 