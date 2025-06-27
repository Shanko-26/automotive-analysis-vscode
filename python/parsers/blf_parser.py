"""
BLF/ASC file parser using python-can library
Handles BLF (Binary Logging Format) and ASC files for CAN bus data
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime

from models.data_models import FileInfo, SignalInfo, SignalData, ChannelInfo

logger = logging.getLogger(__name__)

class BLFParser:
    """Parser for BLF/ASC files using python-can library"""
    
    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            logger.info("BLF Parser initialized successfully")
        else:
            logger.warning("BLF Parser not available - python-can not installed or incompatible with Python 3.12")
    
    def is_available(self) -> bool:
        """Check if the BLF parser is available"""
        return self._available
    
    def _check_availability(self) -> bool:
        """Check if python-can is available"""
        try:
            import can
            logger.info(f"python-can version: {can.__version__}")
            return True
        except ImportError as e:
            logger.warning(f"python-can import failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"python-can initialization failed: {e}")
            return False
    
    async def get_file_info(self, file_path: Path) -> FileInfo:
        """Get file metadata and information"""
        if not self._available:
            # Return basic file info without parsing
            return self._get_basic_file_info(file_path)
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_file_info_sync, file_path)
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            # Fallback to basic file info
            return self._get_basic_file_info(file_path)
    
    def _get_basic_file_info(self, file_path: Path) -> FileInfo:
        """Get basic file information without parsing"""
        file_size = file_path.stat().st_size
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.blf':
            file_type = "BLF"
        elif file_extension == '.asc':
            file_type = "ASC"
        else:
            file_type = file_extension.upper()
        
        return FileInfo(
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            duration=0.0,  # Unknown without parser
            signal_count=0,  # Unknown without parser
            recording_date=None,
            measurement_system="CAN Logger",
            channels=[]
        )
    
    def _get_file_info_sync(self, file_path: Path) -> FileInfo:
        """Synchronous file info extraction"""
        try:
            import can
        except ImportError:
            return self._get_basic_file_info(file_path)
        
        file_size = file_path.stat().st_size
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.blf':
            file_type = "BLF"
            # BLF files need special handling
            duration = 0.0
            recording_date = None
            channels = []
            signal_count = 0
            
            try:
                # Try to read BLF file
                with can.BLFReader(file_path) as reader:
                    messages = list(reader)
                    if messages:
                        # Calculate duration from first and last message
                        start_time = messages[0].timestamp
                        end_time = messages[-1].timestamp
                        duration = end_time - start_time
                        
                        # Get unique CAN IDs as channels
                        can_ids = set(msg.arbitration_id for msg in messages)
                        signal_count = len(can_ids)
                        
                        for can_id in can_ids:
                            # Get messages for this ID
                            id_messages = [msg for msg in messages if msg.arbitration_id == can_id]
                            if id_messages:
                                # Calculate statistics
                                dlc_values = [msg.dlc for msg in id_messages]
                                data_lengths = [len(msg.data) for msg in id_messages]
                                
                                channel_info = ChannelInfo(
                                    name=f"CAN_{can_id:03X}",
                                    unit="",
                                    sample_rate=len(id_messages) / duration if duration > 0 else 0.0,
                                    min_value=float(min(dlc_values)),
                                    max_value=float(max(dlc_values)),
                                    description=f"CAN ID 0x{can_id:03X}",
                                    source="CAN Bus"
                                )
                                channels.append(channel_info)
            
            except Exception as e:
                logger.warning(f"Error reading BLF file {file_path}: {e}")
                
        elif file_extension == '.asc':
            file_type = "ASC"
            # ASC files are text-based
            duration = 0.0
            recording_date = None
            channels = []
            signal_count = 0
            
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    
                    # Parse ASC header for date
                    for line in lines[:10]:  # Check first 10 lines
                        if line.startswith('date'):
                            try:
                                date_str = line.split('date')[1].strip()
                                recording_date = datetime.fromisoformat(date_str)
                            except:
                                pass
                    
                    # Count CAN messages and IDs
                    can_ids = set()
                    for line in lines:
                        if line.strip() and not line.startswith('//') and not line.startswith('date'):
                            try:
                                # Parse CAN message line
                                parts = line.split()
                                if len(parts) >= 4:
                                    can_id = int(parts[2], 16)  # CAN ID in hex
                                    can_ids.add(can_id)
                            except:
                                continue
                    
                    signal_count = len(can_ids)
                    
                    for can_id in can_ids:
                        channel_info = ChannelInfo(
                            name=f"CAN_{can_id:03X}",
                            unit="",
                            sample_rate=0.0,  # Would need to parse full file to calculate
                            min_value=0.0,
                            max_value=8.0,  # Standard CAN DLC range
                            description=f"CAN ID 0x{can_id:03X}",
                            source="CAN Bus"
                        )
                        channels.append(channel_info)
            
            except Exception as e:
                logger.warning(f"Error reading ASC file {file_path}: {e}")
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return FileInfo(
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            duration=duration,
            signal_count=signal_count,
            recording_date=recording_date,
            measurement_system="CAN Logger",
            channels=channels
        )
    
    async def get_signals(self, file_path: Path) -> SignalInfo:
        """Get available signals from the file"""
        if not self._available:
            # Return empty signal info
            return SignalInfo(
                file_path=str(file_path),
                channels=[],
                total_channels=0
            )
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_signals_sync, file_path)
        except Exception as e:
            logger.error(f"Error getting signals for {file_path}: {e}")
            return SignalInfo(
                file_path=str(file_path),
                channels=[],
                total_channels=0
            )
    
    def _get_signals_sync(self, file_path: Path) -> SignalInfo:
        """Synchronous signal extraction"""
        # Reuse file info logic to get channels
        try:
            file_info = self._get_file_info_sync(file_path)
        except Exception as e:
            logger.error(f"Error getting signals for {file_path}: {e}")
            return SignalInfo(
                file_path=str(file_path),
                channels=[],
                total_channels=0
            )
        
        return SignalInfo(
            file_path=str(file_path),
            channels=file_info.channels,
            total_channels=len(file_info.channels)
        )
    
    async def get_signal_data(
        self, 
        file_path: Path, 
        signals: List[str], 
        start_time: Optional[float] = None, 
        end_time: Optional[float] = None
    ) -> SignalData:
        """Get signal data for specified time range"""
        if not self._available:
            # Return empty signal data
            return SignalData(
                file_path=str(file_path),
                signals=signals,
                timestamps=[],
                data={},
                start_time=0.0,
                end_time=0.0,
                sample_count=0
            )
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self._get_signal_data_sync, 
                file_path, 
                signals, 
                start_time, 
                end_time
            )
        except Exception as e:
            logger.error(f"Error getting signal data for {file_path}: {e}")
            return SignalData(
                file_path=str(file_path),
                signals=signals,
                timestamps=[],
                data={},
                start_time=0.0,
                end_time=0.0,
                sample_count=0
            )
    
    def _get_signal_data_sync(
        self, 
        file_path: Path, 
        signals: List[str], 
        start_time: Optional[float] = None, 
        end_time: Optional[float] = None
    ) -> SignalData:
        """Synchronous signal data extraction"""
        try:
            import can
        except ImportError:
            return SignalData(
                file_path=str(file_path),
                signals=signals,
                timestamps=[],
                data={},
                start_time=0.0,
                end_time=0.0,
                sample_count=0
            )
        
        file_extension = file_path.suffix.lower()
        signal_data = {}
        timestamps = []
        
        if file_extension == '.blf':
            try:
                with can.BLFReader(file_path) as reader:
                    messages = list(reader)
                    
                    if not messages:
                        raise ValueError("No messages found in BLF file")
                    
                    # Filter by time range
                    if start_time is not None or end_time is not None:
                        filtered_messages = []
                        for msg in messages:
                            if start_time is None or msg.timestamp >= start_time:
                                if end_time is None or msg.timestamp <= end_time:
                                    filtered_messages.append(msg)
                        messages = filtered_messages
                    
                    # Extract data for each signal
                    for signal_name in signals:
                        if signal_name.startswith('CAN_'):
                            try:
                                can_id = int(signal_name[4:], 16)  # Extract CAN ID
                                signal_messages = [msg for msg in messages if msg.arbitration_id == can_id]
                                
                                # Extract DLC values as signal data
                                signal_data[signal_name] = [msg.dlc for msg in signal_messages]
                                
                                # Use timestamps from first signal
                                if not timestamps:
                                    timestamps = [msg.timestamp for msg in signal_messages]
                                    
                            except Exception as e:
                                logger.warning(f"Failed to extract signal {signal_name}: {e}")
                                signal_data[signal_name] = []
                    
                    # Set time range
                    if messages:
                        actual_start = messages[0].timestamp
                        actual_end = messages[-1].timestamp
                    else:
                        actual_start = actual_end = 0.0
                        
            except Exception as e:
                logger.error(f"Error reading BLF file {file_path}: {e}")
                actual_start = actual_end = 0.0
                
        elif file_extension == '.asc':
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Parse ASC messages
                messages = []
                for line in lines:
                    if line.strip() and not line.startswith('//') and not line.startswith('date'):
                        try:
                            parts = line.split()
                            if len(parts) >= 4:
                                timestamp = float(parts[0])
                                can_id = int(parts[2], 16)
                                dlc = int(parts[3])
                                
                                # Filter by time range
                                if start_time is None or timestamp >= start_time:
                                    if end_time is None or timestamp <= end_time:
                                        messages.append({
                                            'timestamp': timestamp,
                                            'can_id': can_id,
                                            'dlc': dlc
                                        })
                        except:
                            continue
                
                # Extract data for each signal
                for signal_name in signals:
                    if signal_name.startswith('CAN_'):
                        try:
                            can_id = int(signal_name[4:], 16)
                            signal_messages = [msg for msg in messages if msg['can_id'] == can_id]
                            
                            signal_data[signal_name] = [msg['dlc'] for msg in signal_messages]
                            
                            if not timestamps:
                                timestamps = [msg['timestamp'] for msg in signal_messages]
                                
                        except Exception as e:
                            logger.warning(f"Failed to extract signal {signal_name}: {e}")
                            signal_data[signal_name] = []
                
                # Set time range
                if messages:
                    actual_start = messages[0]['timestamp']
                    actual_end = messages[-1]['timestamp']
                else:
                    actual_start = actual_end = 0.0
                    
            except Exception as e:
                logger.error(f"Error reading ASC file {file_path}: {e}")
                actual_start = actual_end = 0.0
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return SignalData(
            file_path=str(file_path),
            signals=signals,
            timestamps=timestamps,
            data=signal_data,
            start_time=actual_start,
            end_time=actual_end,
            sample_count=len(timestamps)
        ) 