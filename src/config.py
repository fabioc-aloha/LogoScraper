"""Global Configuration for Company Logo Scraper

Centralized configuration for the logo scraper application.
All configurable parameters are defined here for easy customization.

USAGE:
- Edit this file to set default paths, batch size, parallelism, and service settings.
- All command-line arguments (see --help) override these defaults for a single run.
- Typical workflow: set persistent defaults here, use CLI args for ad-hoc changes.

Key settings:
- INPUT_FILE: Default Excel file path (e.g., C:\\Data\\CompanyListForLogos.xlsx)
- OUTPUT_FOLDER: Where processed logos are saved (e.g., C:\\Data\\logo)
- BATCH_SIZE: Companies per batch (default: 300)
- MAX_PROCESSES: Parallelism (default: 8)
- OUTPUT_SIZE: Logo size in px (default: 256)
- MAX_RETRIES, RETRY_DELAY: HTTP retry logic
- Filenames for progress and failed domains caches
"""

import os

# Import version information from __version__.py
try:
    from .__version__ import __version__
except ImportError:
    __version__ = "unknown"

# Set base directory for data storage
BASE_DATA_DIR = "C:\\Data"

# Root directory of the project for local temp files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    # Base directories
    'BASE_DATA_DIR': BASE_DATA_DIR,  # Base directory for data storage
    'PROJECT_ROOT': PROJECT_ROOT,    # Project root directory

    # Output and Processing
    'OUTPUT_SIZE': 256,  # Target size (width and height) in pixels for all processed logos
                        # Recommended range: 256-1024. Below 256 may reduce readability; above 1024 increases storage.
    'MIN_SOURCE_SIZE': 24,  # Minimum source image dimension in pixels
                           # At least one dimension (width or height) must be >= this value.
                           # Filters out very small images that would produce poor quality results.
    'BATCH_SIZE': 300,      # Number of companies to process in each parallel batch
                           # For systems with 16GB RAM, 100-500 is optimal. Larger values may cause memory pressure.
    'OUTPUT_FOLDER': os.path.join(BASE_DATA_DIR, 'logo'),  # Directory where processed logos are saved
                                                         # Will be created if it doesn't exist
                                                         # Default: C:\\Data\\logo
    'INPUT_FILE': os.path.join(BASE_DATA_DIR, 'CompanyListForLogos.xlsx'),  # Excel file containing company data
                                                                            # Must include ID, CompanyName, WebsiteURL, and Country columns
                                                                            # For sample data, see example_companies.csv in project root
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),  # Temporary files directory
                                                       # Stores logs, progress files, and temporary data
                                                       # Default: {project_root}\\temp

    # Service Configuration
    'CLEARBIT_RATE_LIMIT': 1600,  # Requests per second limit for Clearbit API
                                  # This is a high value because Clearbit has CDN-level rate limiting
                                  # Adjust downward if you encounter 429 errors
    'CLEARBIT_BASE_URL': 'https://logo.clearbit.com',  # Clearbit Logo API endpoint
                                                      # Public, free API; no authentication required
                                                      # Format: https://logo.clearbit.com/{domain}?size={size}

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,   # Timeout in seconds for HTTP requests
                            # Lower values (5-8) improve responsiveness for failed requests
                            # Higher values (15-30) may help with slow connections
                            # Too low may cause unnecessary failures on slower networks
    'MAX_RETRIES': 3,        # Maximum number of retry attempts for failed requests
                            # Combined with exponential backoff for transient failures
                            # 2-5 is optimal; higher values rarely provide additional benefits
                            # Each retry uses RETRY_DELAY * (2^attempt) seconds
    'RETRY_DELAY': 1.0,      # Base delay between retry attempts in seconds
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
    'PROGRESS_FILE': 'download_progress.json',                 # Stores processing state between runs
                                                              # Enables resuming interrupted operations
                                                              # Delete to restart processing from scratch

    # Processing Defaults
    'MAX_PROCESSES': 4  # Maximum parallel processes for company processing
                        # Recommended: CPU cores - 1 for typical systems
                        # Lower if experiencing memory pressure
                        # Increase for CPU-bound workloads on systems with many cores (12+)
}