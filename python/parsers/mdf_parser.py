"""
MDF/MF4 file parser using asammdf library
Handles MDF3 and MDF4 file formats for automotive measurement data
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime

from models.data_models import FileInfo, SignalInfo, SignalData, ChannelInfo

logger = logging.getLogger(__name__)

class MDFParser:
    """Parser for MDF/MF4 files using asammdf library"""
    
    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            logger.info("MDF Parser initialized successfully")
        else:
            logger.warning("MDF Parser not available - asammdf not installed or incompatible with Python 3.12")
    
    def is_available(self) -> bool:
        """Check if the MDF parser is available"""
        return self._available
    
    def _check_availability(self) -> bool:
        """Check if asammdf is available"""
        try:
            import asammdf
            # Test basic functionality
            logger.info(f"asammdf version: {asammdf.__version__}")
            return True
        except ImportError as e:
            logger.warning(f"asammdf import failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"asammdf initialization failed: {e}")
            return False
    
    async def get_file_info(self, file_path: Path) -> FileInfo:
        """Get file metadata and information"""
        if not self._available:
            # Return basic file info without parsing
            return self._get_basic_file_info(file_path)
        
        try:
            # Use asyncio to run the blocking operation
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
        
        if file_extension in ['.mdf', '.mf4']:
            file_type = f"MDF{file_extension.upper()}"
        else:
            file_type = file_extension.upper()
        
        return FileInfo(
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            duration=0.0,  # Unknown without parser
            signal_count=0,  # Unknown without parser
            recording_date=None,
            measurement_system=None,
            channels=[]
        )
    
    def _get_file_info_sync(self, file_path: Path) -> FileInfo:
        """Synchronous file info extraction"""
        try:
            import asammdf
        except ImportError:
            return self._get_basic_file_info(file_path)
        
        try:
            with asammdf.MDF(file_path) as mdf:
                # Get basic file information
                file_size = file_path.stat().st_size
                file_type = f"MDF{mdf.version}"
                
                # Get time information
                if hasattr(mdf.header, 'start_time') and mdf.header.start_time:
                    recording_date = datetime.fromtimestamp(mdf.header.start_time.timestamp())
                else:
                    recording_date = None
                
                # Calculate duration from measurement data
                duration = 0.0
                try:
                    # Get the first available channel to calculate duration
                    for group in mdf.groups:
                        if group.channels:
                            # Get master channel (timestamps)
                            master = mdf.get_master(group.index)
                            if len(master) > 0:
                                duration = float(master[-1] - master[0])
                                break
                except Exception:
                    # Fallback: try to use start_time property if available
                    try:
                        if hasattr(mdf, 'start_time'):
                            # Calculate from measurement info
                            all_timestamps = []
                            for group in mdf.groups:
                                try:
                                    master = mdf.get_master(group.index)
                                    if len(master) > 0:
                                        all_timestamps.extend([master[0], master[-1]])
                                except Exception:
                                    continue
                            if all_timestamps:
                                duration = float(max(all_timestamps) - min(all_timestamps))
                    except Exception:
                        duration = 0.0
                
                # Get channel information
                channels = []
                signal_count = 0
                
                for group in mdf.groups:
                    for channel in group.channels:
                        if channel.name and not channel.name.startswith('#'):
                            signal_count += 1
                            
                            # Get channel statistics
                            try:
                                signal = mdf.get(channel.name)
                                if signal is not None and hasattr(signal, 'samples'):
                                    min_val = float(np.min(signal.samples))
                                    max_val = float(np.max(signal.samples))
                                    # Handle sample rate calculation more carefully
                                    if hasattr(signal, 'sampling_rate') and signal.sampling_rate:
                                        sample_rate = float(signal.sampling_rate)
                                    elif hasattr(signal, 'timestamps') and len(signal.timestamps) > 1:
                                        # Calculate from timestamps
                                        dt = signal.timestamps[1] - signal.timestamps[0]
                                        sample_rate = 1.0 / dt if dt > 0 else 0.0
                                    else:
                                        sample_rate = 0.0
                                else:
                                    min_val = max_val = sample_rate = 0.0
                            except Exception as e:
                                logger.debug(f"Error processing channel {channel.name}: {e}")
                                min_val = max_val = sample_rate = 0.0
                            
                            channel_info = ChannelInfo(
                                name=channel.name,
                                unit=getattr(channel, 'unit', '') or "",
                                sample_rate=sample_rate,
                                min_value=min_val,
                                max_value=max_val,
                                description=getattr(channel, 'comment', None) or None,
                                source=getattr(channel, 'source', None) or None
                            )
                            channels.append(channel_info)
                
                return FileInfo(
                    file_path=str(file_path),
                    file_size=file_size,
                    file_type=file_type,
                    duration=duration,
                    signal_count=signal_count,
                    recording_date=recording_date,
                    measurement_system=None,  # MDF doesn't always provide this
                    channels=channels
                )
        except Exception as e:
            logger.error(f"Error parsing MDF file {file_path}: {e}")
            return self._get_basic_file_info(file_path)
    
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
        try:
            import asammdf
        except ImportError:
            return SignalInfo(
                file_path=str(file_path),
                channels=[],
                total_channels=0
            )
        
        try:
            with asammdf.MDF(file_path) as mdf:
                channels = []
                
                for group in mdf.groups:
                    for channel in group.channels:
                        if channel.name and not channel.name.startswith('#'):
                            # Get channel statistics
                            try:
                                signal = mdf.get(channel.name)
                                if signal is not None and hasattr(signal, 'samples'):
                                    min_val = float(np.min(signal.samples))
                                    max_val = float(np.max(signal.samples))
                                    # Handle sample rate calculation more carefully
                                    if hasattr(signal, 'sampling_rate') and signal.sampling_rate:
                                        sample_rate = float(signal.sampling_rate)
                                    elif hasattr(signal, 'timestamps') and len(signal.timestamps) > 1:
                                        # Calculate from timestamps
                                        dt = signal.timestamps[1] - signal.timestamps[0]
                                        sample_rate = 1.0 / dt if dt > 0 else 0.0
                                    else:
                                        sample_rate = 0.0
                                else:
                                    min_val = max_val = sample_rate = 0.0
                            except Exception as e:
                                logger.debug(f"Error processing channel {channel.name}: {e}")
                                min_val = max_val = sample_rate = 0.0
                            
                            channel_info = ChannelInfo(
                                name=channel.name,
                                unit=getattr(channel, 'unit', '') or "",
                                sample_rate=sample_rate,
                                min_value=min_val,
                                max_value=max_val,
                                description=getattr(channel, 'comment', None) or None,
                                source=getattr(channel, 'source', None) or None
                            )
                            channels.append(channel_info)
                
                return SignalInfo(
                    file_path=str(file_path),
                    channels=channels,
                    total_channels=len(channels)
                )
        except Exception as e:
            logger.error(f"Error parsing MDF signals {file_path}: {e}")
            return SignalInfo(
                file_path=str(file_path),
                channels=[],
                total_channels=0
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
            import asammdf
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
        
        try:
            with asammdf.MDF(file_path) as mdf:
                # Get time range
                if start_time is None or end_time is None:
                    # Get full time range
                    if mdf.header.start_time and mdf.header.end_time:
                        start_time = 0.0
                        end_time = (mdf.header.end_time - mdf.header.start_time).total_seconds()
                    else:
                        start_time = 0.0
                        end_time = 0.0
                
                # Extract data for each signal
                signal_data = {}
                timestamps = None
                
                for signal_name in signals:
                    try:
                        signal = mdf.get(signal_name, time_from=start_time, time_to=end_time)
                        if signal is not None:
                            # Convert to list for JSON serialization
                            signal_data[signal_name] = signal.samples.tolist()
                            
                            # Use first signal's timestamps as reference
                            if timestamps is None:
                                timestamps = signal.timestamps.tolist()
                    except Exception as e:
                        logger.warning(f"Failed to extract signal {signal_name}: {e}")
                        signal_data[signal_name] = []
                
                # If no timestamps available, create a simple time array
                if timestamps is None:
                    max_samples = max(len(data) for data in signal_data.values()) if signal_data else 0
                    timestamps = list(np.linspace(start_time, end_time, max_samples))
                
                return SignalData(
                    file_path=str(file_path),
                    signals=signals,
                    timestamps=timestamps,
                    data=signal_data,
                    start_time=start_time,
                    end_time=end_time,
                    sample_count=len(timestamps)
                )
        except Exception as e:
            logger.error(f"Error parsing MDF data {file_path}: {e}")
            return SignalData(
                file_path=str(file_path),
                signals=signals,
                timestamps=[],
                data={},
                start_time=0.0,
                end_time=0.0,
                sample_count=0
            ) 