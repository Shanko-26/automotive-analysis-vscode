"""
Data chunking utilities for efficient handling of large measurement files
Provides memory-efficient data access patterns for large datasets
"""

import logging
from typing import List, Optional, Dict, Any, Generator
import numpy as np

logger = logging.getLogger(__name__)

class DataChunker:
    """Utility class for chunking large datasets into manageable pieces"""
    
    def __init__(self, chunk_size: int = 10000):
        """
        Initialize the data chunker
        
        Args:
            chunk_size: Number of samples per chunk (default: 10,000)
        """
        self.chunk_size = chunk_size
        logger.info(f"DataChunker initialized with chunk size: {chunk_size}")
    
    def chunk_array(self, data: np.ndarray, start_idx: int = 0, end_idx: Optional[int] = None) -> Generator[np.ndarray, None, None]:
        """
        Split a numpy array into chunks
        
        Args:
            data: Input array to chunk
            start_idx: Starting index (inclusive)
            end_idx: Ending index (exclusive), None for end of array
            
        Yields:
            Chunks of the input array
        """
        if end_idx is None:
            end_idx = len(data)
        
        for i in range(start_idx, end_idx, self.chunk_size):
            chunk_end = min(i + self.chunk_size, end_idx)
            yield data[i:chunk_end]
    
    def chunk_time_range(self, total_duration: float, chunk_duration: Optional[float] = None) -> Generator[tuple, None, None]:
        """
        Generate time range chunks for large datasets
        
        Args:
            total_duration: Total duration in seconds
            chunk_duration: Duration of each chunk in seconds (default: calculated from chunk_size)
            
        Yields:
            Tuples of (start_time, end_time) for each chunk
        """
        if chunk_duration is None:
            # Estimate chunk duration based on typical sample rate
            # Assuming 100Hz sample rate for estimation
            estimated_samples_per_chunk = self.chunk_size
            chunk_duration = estimated_samples_per_chunk / 100.0
        
        current_time = 0.0
        while current_time < total_duration:
            end_time = min(current_time + chunk_duration, total_duration)
            yield (current_time, end_time)
            current_time = end_time
    
    def get_optimal_chunk_size(self, file_size_bytes: int, available_memory_bytes: int) -> int:
        """
        Calculate optimal chunk size based on available memory
        
        Args:
            file_size_bytes: Size of the file in bytes
            available_memory_bytes: Available memory in bytes
            
        Returns:
            Optimal chunk size in samples
        """
        # Use 10% of available memory for data chunks
        memory_for_chunks = available_memory_bytes * 0.1
        
        # Estimate bytes per sample (assuming float64)
        bytes_per_sample = 8
        
        # Calculate optimal chunk size
        optimal_chunk_size = int(memory_for_chunks / bytes_per_sample)
        
        # Ensure reasonable bounds
        optimal_chunk_size = max(1000, min(optimal_chunk_size, 100000))
        
        logger.info(f"Optimal chunk size calculated: {optimal_chunk_size} samples")
        return optimal_chunk_size
    
    def estimate_processing_time(self, total_samples: int, sample_rate: float) -> float:
        """
        Estimate processing time for a dataset
        
        Args:
            total_samples: Total number of samples
            sample_rate: Sample rate in Hz
            
        Returns:
            Estimated processing time in seconds
        """
        # Rough estimation: 1ms per chunk
        num_chunks = (total_samples + self.chunk_size - 1) // self.chunk_size
        processing_time = num_chunks * 0.001
        
        logger.info(f"Estimated processing time: {processing_time:.2f}s for {total_samples} samples")
        return processing_time
    
    def create_chunked_data_response(self, data: Dict[str, np.ndarray], timestamps: np.ndarray) -> Dict[str, Any]:
        """
        Create a response with chunked data information
        
        Args:
            data: Dictionary of signal data arrays
            timestamps: Time array
            
        Returns:
            Dictionary with chunked data information
        """
        total_samples = len(timestamps)
        num_chunks = (total_samples + self.chunk_size - 1) // self.chunk_size
        
        chunk_info = {
            "total_samples": total_samples,
            "chunk_size": self.chunk_size,
            "num_chunks": num_chunks,
            "estimated_processing_time": self.estimate_processing_time(total_samples, 100.0),  # Assume 100Hz
            "chunks": []
        }
        
        # Create chunk information
        for i in range(num_chunks):
            start_idx = i * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, total_samples)
            
            chunk = {
                "chunk_index": i,
                "start_index": start_idx,
                "end_index": end_idx,
                "start_time": float(timestamps[start_idx]) if start_idx < len(timestamps) else 0.0,
                "end_time": float(timestamps[end_idx - 1]) if end_idx > 0 and end_idx - 1 < len(timestamps) else 0.0,
                "sample_count": end_idx - start_idx
            }
            chunk_info["chunks"].append(chunk)
        
        return chunk_info 