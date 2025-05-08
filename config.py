"""Global Configuration for Logo Scraper

This module provides centralized configuration for the logo scraper application.
All configurable parameters are defined here to allow easy customization.
"""

import os

# Set base directory for data storage to C:\Data
BASE_DATA_DIR = r'C:\Data'

# Root directory of the project for local temp files
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    # Output and Processing
    'OUTPUT_SIZE': 512,  # Target size (width and height) in pixels for all processed logos
    'MIN_SOURCE_SIZE': 60,  # Minimum source image dimension in pixels
    'BATCH_SIZE': 300,  # Number of companies to process in each parallel batch
    'OUTPUT_FOLDER': os.path.join(BASE_DATA_DIR, 'logos'),  # Directory where processed logos are saved
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),  # Directory for temporary files during processing
    'INPUT_FILE': os.path.join(BASE_DATA_DIR, 'input', 'Companies.xlsx'),  # Excel file containing company data
    'CORNER_RADIUS': 40,  # Corner radius in pixels for default logo rounded rectangles

    # Logging Configuration
    'LOG_LEVEL': 'INFO',  # Logging level (DEBUG, INFO, WARNING, ERROR)
    'LOG_FORMAT': '%(asctime)s - %(levelname)s - %(message)s',  # Log message format

    # Service Configuration
    ## Clearbit Service
    'CLEARBIT_RATE_LIMIT': 1600,     # requests per second for Clearbit API
    'CLEARBIT_BASE_URL': 'https://logo.clearbit.com',

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,  # Timeout in seconds for HTTP requests
    'MAX_RETRIES': 3,       # Maximum number of retry attempts for failed requests
    'RETRY_DELAY': 1.0,     # Base delay between retry attempts in seconds
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',

    # Filter Columns (lowercase for consistency)
    'FILTER_COLUMNS': {
        'CORE': ['tpid', 'mssalesid', 'crmaccountname', 'websiteurl'],
        'SEGMENTATION': ['industry', 'vertical', 'sector', 'segmentgroup'],
        'GEOGRAPHY': ['country', 'city', 'areaname', 'subsidiaryname'],
        'STATUS': ['accountstatus', 'parentinglevel', 'top_list']
    },

    # Default Filtering Configuration
    'filters': {
        'parentinglevel': 'Top Parent',
        'status': 'Active'
    },
    # Limit to top N rows for testing
    # 'TOP_N': 400,

    # Filenames and prefixes
    'FAILED_DOMAINS_CACHE_FILE': 'failed_domains_cache.json',  # Cache for domains that failed processing
    'PROGRESS_FILE': 'download_progress.json',  # Progress tracking file name
    'ENRICHED_FILENAME_PREFIX': 'Companies_Enriched_',  # Prefix for enriched output files
    'LOG_FILENAME': 'logo_scraper.log',  # Default log file name

    # Processing Defaults
    'MAX_PROCESSES': 8  # Maximum parallel processes
}