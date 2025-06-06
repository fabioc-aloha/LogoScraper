"""Configuration Validation Module

This module provides configuration validation functionality.
"""

import os
import logging
import sys
from typing import List, Dict

# Add parent directory to sys.path to allow importing config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONFIG  # Import the configuration

class ConfigValidator:
    """Validates configuration settings."""

    def __init__(self, config: Dict):
        """Initialize the validator."""
        self.config = config
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Validate all configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        self._validate_paths()
        self._validate_sizes()
        self._validate_rate_limits()
        self._validate_required_fields()
        
        # Log all warnings and errors
        for warning in self.warnings:
            logging.warning(f"Configuration warning: {warning}")
        for error in self.errors:
            logging.error(f"Configuration error: {error}")
            
        return len(self.errors) == 0

    def _validate_paths(self):
        """Validate path configurations."""
        # Check output folder
        output_folder = self.config.get('OUTPUT_FOLDER')
        if not output_folder:
            self.errors.append("OUTPUT_FOLDER not configured")
        elif not os.path.exists(os.path.dirname(output_folder)):
            self.errors.append(f"Parent directory for OUTPUT_FOLDER does not exist: {output_folder}")
            
        # Check input file
        input_file = self.config.get('INPUT_FILE')
        if not input_file:
            self.errors.append("INPUT_FILE not configured")
        elif not os.path.exists(os.path.dirname(input_file)):
            self.errors.append(f"Parent directory for INPUT_FILE does not exist: {input_file}")

    def _validate_sizes(self):
        """Validate size configurations."""
        # Check output size
        output_size = self.config.get('OUTPUT_SIZE')
        if not output_size:
            self.errors.append("OUTPUT_SIZE not configured")
        elif not isinstance(output_size, int) or output_size < 1:
            self.errors.append(f"Invalid OUTPUT_SIZE: {output_size}")
        elif output_size < 100:
            self.warnings.append(f"OUTPUT_SIZE may be too small: {output_size}")
        elif output_size > 1024:
            self.warnings.append(f"OUTPUT_SIZE may be too large: {output_size}")
            
        # Check minimum source size
        min_size = self.config.get('MIN_SOURCE_SIZE')
        if not min_size:
            self.errors.append("MIN_SOURCE_SIZE not configured")
        elif not isinstance(min_size, int) or min_size < 1:
            self.errors.append(f"Invalid MIN_SOURCE_SIZE: {min_size}")
        elif min_size < 32:
            self.warnings.append(f"MIN_SOURCE_SIZE may be too small: {min_size}")

    def _validate_rate_limits(self):
        """Validate rate limit configurations."""
        # Check Clearbit rate limit
        clearbit_limit = self.config.get('CLEARBIT_RATE_LIMIT')
        if not clearbit_limit:
            self.errors.append("CLEARBIT_RATE_LIMIT not configured")
        elif not isinstance(clearbit_limit, int) or clearbit_limit < 1:
            self.errors.append(f"Invalid CLEARBIT_RATE_LIMIT: {clearbit_limit}")

    def _validate_required_fields(self):
        """Validate required field configurations."""
        required_fields = {
            'USER_AGENT': str,
            'REQUEST_TIMEOUT': int,
            'BATCH_SIZE': int,
            'LOG_LEVEL': str,
            'LOG_FORMAT': str
            # 'CORNER_RADIUS': int
        }
        
        for field, expected_type in required_fields.items():
            value = self.config.get(field)
            if not value:
                self.errors.append(f"{field} not configured")
            elif not isinstance(value, expected_type):
                self.errors.append(f"Invalid type for {field}: expected {expected_type.__name__}, got {type(value).__name__}")

    def get_status(self) -> Dict:
        """Get validation status.
        
        Returns:
            Dict containing validation results
        """
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for configuration validation.
    
    This function demonstrates how to use the ConfigValidator class
    and can be run directly to validate the current configuration.
    """
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create validator instance with current configuration
    validator = ConfigValidator(CONFIG)
    
    # Run validation
    is_valid = validator.validate()
    
    # Get detailed status
    status = validator.get_status()
    
    # Print results
    if is_valid:
        logging.info("Configuration validation successful")
    else:
        logging.error("Configuration validation failed")
        
    if status['warnings']:
        logging.info("Warnings found:")
        for warning in status['warnings']:
            logging.warning(f"- {warning}")
            
    if status['errors']:
        logging.info("Errors found:")
        for error in status['errors']:
            logging.error(f"- {error}")
    
    return is_valid

if __name__ == '__main__':
    main()