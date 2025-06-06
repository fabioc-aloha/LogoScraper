"""Global Configuration for Logo Scraper

This module provides centralized configuration for the logo scraper application.
All configurable parameters are defined here to allow easy customization.

USAGE:
- Edit this file to set default paths, batch size, parallelism, logging, and service settings.
- All command-line arguments (see --help) override these defaults for a single run.
- Typical workflow: set persistent defaults here, use CLI args for ad-hoc changes.

Key settings:
- INPUT_FILE: Default Excel file path (e.g., C:\\Data\\input\\Companies.xlsx)
- OUTPUT_FOLDER: Where processed logos are saved (e.g., C:\\Data\\logo)
- TEMP_FOLDER: Where temp files/logs are stored (default: project temp/)
- BATCH_SIZE: Companies per batch (default: 300)
- MAX_PROCESSES: Parallelism (default: 8)
- LOG_LEVEL: Logging level (default: INFO)
- OUTPUT_SIZE: Logo size in px (default: 256)
- MAX_RETRIES, RETRY_DELAY: HTTP retry logic
- Filenames for progress and failed domains caches
"""

import os

# Import version information
try:
    from .__version__ import __version__, __build_date__, __features__
except ImportError:
    __version__ = "unknown"
    __build_date__ = "unknown"
    __features__ = {}

# Set base directory for data storage to C:\Data
BASE_DATA_DIR = r'C:\Data'

# Root directory of the project for local temp files
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    # Version and Build Information
    'VERSION': __version__,
    'BUILD_DATE': __build_date__,
    'FEATURES': __features__,
    
    # Output and Processing
    'OUTPUT_SIZE': 256,  # Target size (width and height) in pixels for all processed logos
                         # Recommended range: 256-1024. Values below 256 may result in poor text readability.
                         # Values above 1024 significantly increase storage requirements without proportional quality gains.
                         
    'MIN_SOURCE_SIZE': 24,  # Minimum source image dimension in pixels
                            # At least one dimension (width or height) must be >= this value.
                            # This filters out very small source images that would produce poor quality results.
                            # Values below 24 may allow low-quality images; above 100 may reject too many valid sources.
                            
    'BATCH_SIZE': 300,  # Number of companies to process in each parallel batch
                        # Determines memory usage and CPU utilization. For systems with 16GB RAM,
                        # values between 100-500 are optimal. Larger values may cause memory pressure.
                          'OUTPUT_FOLDER': os.path.join(BASE_DATA_DIR, 'logo'),  # Directory where processed logos are saved
                                                           # Will be created if it doesn't exist
                                                           
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),  # Directory for temporary files during processing
                                                        # Used for caching, progress tracking, and logs
                                                        # Contents can be safely deleted between runs
                                                        
    'INPUT_FILE': os.path.join(BASE_DATA_DIR, 'input', 'Companies.xlsx'),  # Excel file containing company data
                                                                           # Must include tpid and crmaccountname columns

    # Logging Configuration
    'LOG_LEVEL': 'ERROR',  # Logging level (DEBUG, INFO, WARNING, ERROR)
                          # Use DEBUG for development and troubleshooting
                          # Use INFO for normal operation
                          # Use WARNING or ERROR for production to minimize log size
                            'LOG_FORMAT': '%(asctime)s - %(levelname)s - %(message)s',  # Log message format
                                                               # Includes timestamp, severity level, and message
                                                               
    # Service Configuration
    ## Clearbit Service
    'CLEARBIT_RATE_LIMIT': 1600,     # Requests per second limit for Clearbit API
                                     # This is a high value because Clearbit has CDN-level rate limiting
                                     # Adjust downward if you encounter 429 errors
    
    'CLEARBIT_BASE_URL': 'https://logo.clearbit.com',  # Clearbit Logo API endpoint
                                                       # This is a public, free API that doesn't require authentication
                                                       # Format: https://logo.clearbit.com/{domain}?size={size}

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,  # Timeout in seconds for HTTP requests
                           # Lower values (5-8) improve responsiveness for failed requests
                           # Higher values (15-30) may help with slow connections
                           # Too low may cause unnecessary failures on slower networks
                           
    'MAX_RETRIES': 3,       # Maximum number of retry attempts for failed requests
                           # Combined with exponential backoff for transient failures
                           # 2-5 is optimal; higher values rarely provide additional benefits
                           # Each retry uses RETRY_DELAY * (2^attempt) seconds
                           
    'RETRY_DELAY': 1.0,     # Base delay between retry attempts in seconds
                           # First retry: 1s, Second: 2s, Third: 4s (with default MAX_RETRIES=3)
                           # Increase for APIs with strict rate-limiting
                             'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                  # User agent string for HTTP requests
                  # Using a standard browser UA improves compatibility with some services
                  # Change only if you encounter specific blocking issues
                  
    # Filenames and prefixes
    'FAILED_DOMAINS_CACHE_FILE': 'failed_domains_cache.json',  # Persists domains with failed lookups
                                                              # Prevents repeated attempts at domains known to fail
                                                              # Delete this file to reset and retry all domains
                                                              
    'PROGRESS_FILE': 'download_progress.json',  # Stores processing state between runs
                                               # Enables resuming interrupted operations
                                               # Delete to restart processing from scratch
                                               
    'ENRICHED_FILENAME_PREFIX': 'Companies_Enriched_',  # Output filename prefix
                                                       # Will be followed by timestamp
                                                       # Format: {prefix}{YYYYMMDD_HHMMSS}.xlsx
                                                       
    'LOG_FILENAME': 'logo_scraper.log',  # Default log file name
                                        # Created in both the execution directory and TEMP_FOLDER
                                        # Provides detailed processing history and error information

    # Processing Defaults
    'MAX_PROCESSES': 8  # Maximum parallel processes for company processing
                        # Recommended setting: CPU cores - 1 for typical systems
                        # Lower this value if experiencing memory pressure
                        # Increase for CPU-bound workloads on systems with many cores (12+)
}