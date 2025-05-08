"""Logging Configuration Module

This module provides consistent logging configuration across the application.
"""

import os
import logging
from config import CONFIG

def setup_logging(temp_folder, log_filename='logo_scraper.log'):
    """Set up logging with consistent configuration.
    
    Args:
        temp_folder: Directory for log files
        log_filename: Name of the log file
    """
    log_file = os.path.join(temp_folder, log_filename)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=CONFIG.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(CONFIG.get('LOG_LEVEL', 'INFO'))
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info("Logging system initialized")