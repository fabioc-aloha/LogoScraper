#!/usr/bin/env python3
"""Test CLI argument configuration flow."""

import sys
import os
import argparse

# Add parent directory to path to access src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import CONFIG

# Import CLI functions from main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import parse_arguments, update_config_from_args

def test_cli_config_flow():
    """Test that CLI arguments properly update CONFIG values."""
    print("Testing CLI argument configuration flow...")
    
    # Store original values
    original_values = {
        'OUTPUT_SIZE': CONFIG['OUTPUT_SIZE'],
        'BATCH_SIZE': CONFIG['BATCH_SIZE'],
        'LOG_LEVEL': CONFIG['LOG_LEVEL'],
        'MAX_PROCESSES': CONFIG['MAX_PROCESSES'],
        'INPUT_FILE': CONFIG['INPUT_FILE'],
        'OUTPUT_FOLDER': CONFIG['OUTPUT_FOLDER'],
        'TEMP_FOLDER': CONFIG['TEMP_FOLDER']
    }
    
    print(f"Original values:")
    for key, value in original_values.items():
        print(f"  {key}: {value}")
    
    # Test CLI argument parsing with mock arguments
    test_args = [
        '--batch-size', '150',
        '--log-level', 'DEBUG',
        '--max-processes', '4',
        '--input', 'C:\\Test\\input.xlsx',
        '--output', 'C:\\Test\\output',
        '--temp', 'C:\\Test\\temp',
        '--top', '500',
        '--filter', 'country=USA',
        '--filter', 'industry=Tech',
        '--tpid', '12345',
        '--tpid', '67890'
    ]
    
    # Mock sys.argv
    original_argv = sys.argv
    sys.argv = ['main.py'] + test_args
    
    try:
        # Parse arguments
        args = parse_arguments()
        print(f"\nParsed arguments:")
        print(f"  batch_size: {args.batch_size}")
        print(f"  log_level: {args.log_level}")
        print(f"  max_processes: {args.max_processes}")
        print(f"  input: {args.input}")
        print(f"  output: {args.output}")
        print(f"  temp: {args.temp}")
        print(f"  top: {args.top}")
        print(f"  filter: {args.filter}")
        print(f"  tpid: {args.tpid}")
        
        # Update config from arguments
        update_config_from_args(args)
        
        print(f"\nUpdated CONFIG values:")
        print(f"  BATCH_SIZE: {CONFIG['BATCH_SIZE']}")
        print(f"  LOG_LEVEL: {CONFIG['LOG_LEVEL']}")
        print(f"  MAX_PROCESSES: {CONFIG['MAX_PROCESSES']}")
        print(f"  INPUT_FILE: {CONFIG['INPUT_FILE']}")
        print(f"  OUTPUT_FOLDER: {CONFIG['OUTPUT_FOLDER']}")
        print(f"  TEMP_FOLDER: {CONFIG['TEMP_FOLDER']}")
        print(f"  TOP_N: {CONFIG.get('TOP_N')}")
        print(f"  filters: {CONFIG.get('filters')}")
        print(f"  tpid_filter: {CONFIG.get('tpid_filter')}")
        
        # Verify updates
        assert CONFIG['BATCH_SIZE'] == 150, f"Expected 150, got {CONFIG['BATCH_SIZE']}"
        assert CONFIG['LOG_LEVEL'] == 'DEBUG', f"Expected DEBUG, got {CONFIG['LOG_LEVEL']}"
        assert CONFIG['MAX_PROCESSES'] == 4, f"Expected 4, got {CONFIG['MAX_PROCESSES']}"
        assert CONFIG['INPUT_FILE'] == 'C:\\Test\\input.xlsx'
        assert CONFIG['OUTPUT_FOLDER'] == 'C:\\Test\\output'
        assert CONFIG['TEMP_FOLDER'] == 'C:\\Test\\temp'
        assert CONFIG.get('TOP_N') == 500
        assert CONFIG.get('filters') == {'country': 'USA', 'industry': 'Tech'}
        assert CONFIG.get('tpid_filter') == ['12345', '67890']
        
        print("\n✅ All CLI argument configuration tests passed!")
        
    finally:
        # Restore original argv
        sys.argv = original_argv
        
        # Restore original config values
        CONFIG.update(original_values)
        
        # Clean up filter keys
        CONFIG.pop('filters', None)
        CONFIG.pop('tpid_filter', None)
        CONFIG.pop('TOP_N', None)
        
        print("\n✅ Configuration values restored to original state")

if __name__ == "__main__":
    test_cli_config_flow()
