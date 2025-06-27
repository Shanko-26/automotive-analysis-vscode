#!/usr/bin/env python3
"""
Basic tests for the automotive analysis backend
"""

import sys
import os
from pathlib import Path

# Add the python directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models.data_models import FileInfo, SignalInfo, SignalData
        print("✅ Data models imported successfully")
        
        from parsers.mdf_parser import MDFParser
        print("✅ MDF parser imported successfully")
        
        from parsers.blf_parser import BLFParser
        print("✅ BLF parser imported successfully")
        
        from utils.chunking import DataChunker
        print("✅ Data chunker imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_parser_availability():
    """Test parser availability"""
    try:
        from parsers.mdf_parser import MDFParser
        from parsers.blf_parser import BLFParser
        
        mdf_parser = MDFParser()
        blf_parser = BLFParser()
        
        print(f"✅ MDF Parser available: {mdf_parser.is_available()}")
        print(f"✅ BLF Parser available: {blf_parser.is_available()}")
        
        return True
    except Exception as e:
        print(f"❌ Parser test error: {e}")
        return False

def test_data_models():
    """Test data model creation"""
    try:
        from models.data_models import FileInfo, ChannelInfo
        
        # Create a test channel
        channel = ChannelInfo(
            name="TestSignal",
            unit="deg",
            sample_rate=100.0,
            min_value=0.0,
            max_value=360.0
        )
        
        # Create a test file info
        file_info = FileInfo(
            file_path="/test/file.mdf",
            file_size=1024,
            file_type="MDF4",
            duration=60.0,
            signal_count=1,
            channels=[channel]
        )
        
        print("✅ Data models created successfully")
        print(f"   File: {file_info.file_path}")
        print(f"   Signals: {file_info.signal_count}")
        print(f"   Duration: {file_info.duration}s")
        
        return True
    except Exception as e:
        print(f"❌ Data model test error: {e}")
        return False

def test_chunking():
    """Test data chunking functionality"""
    try:
        from utils.chunking import DataChunker
        import numpy as np
        
        chunker = DataChunker(chunk_size=1000)
        
        # Create test data
        data = np.random.random(5000)
        
        # Test chunking
        chunks = list(chunker.chunk_array(data))
        print(f"✅ Data chunking test: {len(chunks)} chunks created")
        
        # Test time range chunking
        time_chunks = list(chunker.chunk_time_range(100.0))
        print(f"✅ Time chunking test: {len(time_chunks)} time chunks created")
        
        return True
    except Exception as e:
        print(f"❌ Chunking test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running basic tests for Automotive Analysis Backend\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Parser Availability", test_parser_availability),
        ("Data Models", test_data_models),
        ("Data Chunking", test_chunking)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
        print()
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The backend is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 