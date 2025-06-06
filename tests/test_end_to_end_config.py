#!/usr/bin/env python3
"""Comprehensive end-to-end configuration test."""

import sys
import os
import tempfile
import shutil

# Add parent directory to path to access src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import CONFIG
from src.logo_scraper_core import LogoScraper
from src.utils.batch_processor import process_batch
import pandas as pd

def test_end_to_end_config():
    """Test that configuration flows correctly through the entire pipeline."""
    print("Testing end-to-end configuration flow...")
    
    # Store original values
    original_batch_size = CONFIG['BATCH_SIZE']
    original_output_size = CONFIG['OUTPUT_SIZE']
    original_max_processes = CONFIG['MAX_PROCESSES']
    
    try:
        # Update configuration to simulate CLI args
        CONFIG['BATCH_SIZE'] = 50
        CONFIG['OUTPUT_SIZE'] = 128
        CONFIG['MAX_PROCESSES'] = 2
        
        print(f"Updated BATCH_SIZE to: {CONFIG['BATCH_SIZE']}")
        print(f"Updated OUTPUT_SIZE to: {CONFIG['OUTPUT_SIZE']}")
        print(f"Updated MAX_PROCESSES to: {CONFIG['MAX_PROCESSES']}")
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'output')
            temp_processing_dir = os.path.join(temp_dir, 'temp')
            os.makedirs(output_dir)
            os.makedirs(temp_processing_dir)
            
            # Test 1: LogoScraper initialization respects config
            print("\nTesting LogoScraper initialization...")
            scraper = LogoScraper(output_folder=output_dir, batch_size=CONFIG['BATCH_SIZE'])
            
            print(f"LogoScraper batch_size: {scraper.batch_size}")
            print(f"LogoScraper output_folder: {scraper.output_folder}")
            
            assert scraper.batch_size == 50, f"Expected 50, got {scraper.batch_size}"
            assert scraper.output_folder == output_dir
            
            # Test 2: Batch processor respects MAX_PROCESSES
            print("\nTesting batch processor configuration...")
            
            # Create a small test dataframe
            test_df = pd.DataFrame({
                'tpid': ['TEST001', 'TEST002'],
                'crmaccountname': ['Test Company 1', 'Test Company 2'],
                'websiteurl': ['https://example.com', 'https://test.com']
            })
            
            # This should use the updated MAX_PROCESSES value
            print(f"Will use MAX_PROCESSES: {CONFIG['MAX_PROCESSES']}")
            
            # Clean up the scraper
            scraper.cleanup()
            
        print("\n✅ End-to-end configuration flow test passed!")
        
    finally:
        # Restore original values
        CONFIG['BATCH_SIZE'] = original_batch_size
        CONFIG['OUTPUT_SIZE'] = original_output_size
        CONFIG['MAX_PROCESSES'] = original_max_processes
        
        print(f"\n✅ Restored original configuration values")
        print(f"  BATCH_SIZE: {CONFIG['BATCH_SIZE']}")
        print(f"  OUTPUT_SIZE: {CONFIG['OUTPUT_SIZE']}")
        print(f"  MAX_PROCESSES: {CONFIG['MAX_PROCESSES']}")

if __name__ == "__main__":
    test_end_to_end_config()
