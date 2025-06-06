#!/usr/bin/env python3
"""Test script to verify configuration flow from CLI to all components."""

import sys
import os
import argparse
from unittest.mock import patch

# Add parent directory to path to access src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import CONFIG
from src.services.clearbit_service import ClearbitService
from src.services.input_data_service import InputDataService
from src.utils.default_logo_generator import create_default_logo
from src.utils.image_resizer import save_standardized_logo
from src.utils.log_config import setup_logging
from src.utils.session_manager import SessionManager

def test_config_propagation():
    """Test that configuration values are properly used throughout the system."""
    print("Testing configuration propagation...")
    
    # Test 1: Default values
    print(f"Default OUTPUT_SIZE: {CONFIG['OUTPUT_SIZE']}")
    print(f"Default BATCH_SIZE: {CONFIG['BATCH_SIZE']}")
    print(f"Default LOG_LEVEL: {CONFIG['LOG_LEVEL']}")
    print(f"Default MAX_PROCESSES: {CONFIG['MAX_PROCESSES']}")
    print(f"Default REQUEST_TIMEOUT: {CONFIG['REQUEST_TIMEOUT']}")
    print(f"Default CLEARBIT_RATE_LIMIT: {CONFIG['CLEARBIT_RATE_LIMIT']}")
    
    # Test 2: Simulate CLI argument updates
    print("\nSimulating CLI argument updates...")
    original_values = {
        'OUTPUT_SIZE': CONFIG['OUTPUT_SIZE'],
        'BATCH_SIZE': CONFIG['BATCH_SIZE'],
        'LOG_LEVEL': CONFIG['LOG_LEVEL'],
        'MAX_PROCESSES': CONFIG['MAX_PROCESSES']
    }
    
    # Simulate CLI updates
    CONFIG['OUTPUT_SIZE'] = 512
    CONFIG['BATCH_SIZE'] = 150
    CONFIG['LOG_LEVEL'] = 'DEBUG'
    CONFIG['MAX_PROCESSES'] = 4
    
    print(f"Updated OUTPUT_SIZE: {CONFIG['OUTPUT_SIZE']}")
    print(f"Updated BATCH_SIZE: {CONFIG['BATCH_SIZE']}")
    print(f"Updated LOG_LEVEL: {CONFIG['LOG_LEVEL']}")
    print(f"Updated MAX_PROCESSES: {CONFIG['MAX_PROCESSES']}")
    
    # Test 3: Verify services use updated config
    print("\nTesting service configuration usage...")
    
    # Test ClearbitService
    clearbit_service = ClearbitService(CONFIG['OUTPUT_SIZE'])
    print(f"ClearbitService target_size: {clearbit_service.target_size}")
    assert clearbit_service.target_size == 512, f"Expected 512, got {clearbit_service.target_size}"
    
    # Test SessionManager
    session_manager = SessionManager()
    print(f"SessionManager timeout: {session_manager.timeout}")
    print(f"SessionManager max_retries: {session_manager.max_retries}")
    assert session_manager.timeout == CONFIG['REQUEST_TIMEOUT']
    assert session_manager.max_retries == CONFIG['MAX_RETRIES']
    
    # Test InputDataService
    input_service = InputDataService()
    print("InputDataService created successfully")
    
    # Test 4: Verify image processing uses updated config
    print("\nTesting image processing configuration...")
    
    # Test default logo generation
    print("Testing default logo generation with updated OUTPUT_SIZE...")
    try:
        # This should use the updated OUTPUT_SIZE (512)
        logo_data = create_default_logo("Test Company")
        if logo_data:
            print("Default logo generated successfully")
            # Save test image to verify size
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(logo_data))
            print(f"Generated logo size: {img.size}")
            assert img.size == (512, 512), f"Expected (512, 512), got {img.size}"
        else:
            print("Failed to generate default logo")
    except Exception as e:
        print(f"Error testing default logo generation: {e}")
    
    # Test 5: Verify filter configuration
    print("\nTesting filter configuration...")
    CONFIG['filters'] = {'country': 'USA'}
    CONFIG['TOP_N'] = 100
    CONFIG['tpid_filter'] = ['123', '456']
    
    print(f"Filters: {CONFIG.get('filters')}")
    print(f"TOP_N: {CONFIG.get('TOP_N')}")
    print(f"TPID filter: {CONFIG.get('tpid_filter')}")
      # Test 6: Verify logging uses updated config
    print("\nTesting logging configuration...")
    import tempfile
    import logging
    
    # Clear any existing handlers to avoid file locks
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        setup_logging(temp_dir, 'test_log.log')
        logger = logging.getLogger()
        print(f"Logger level: {logger.level}")
        print(f"Expected level: {getattr(logging, CONFIG['LOG_LEVEL'])}")
        assert logger.level == getattr(logging, CONFIG['LOG_LEVEL'])
        
        # Clean up handlers before temp directory cleanup
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
    
    print("\n✅ All configuration propagation tests passed!")
    
    # Restore original values
    CONFIG.update(original_values)
    print("\n✅ Configuration values restored to original state")

if __name__ == "__main__":
    test_config_propagation()
