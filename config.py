"""Global Configuration for Logo Scraper

This module provides centralized configuration for the logo scraper application.
All configurable parameters are defined here to allow easy customization of the
application's behavior without modifying code.

Configuration categories:
- Output and Processing: Control logo dimensions and batch processing
- Service Rate Limits: API and service request throttling
- HTTP Configuration: Network request settings
- Favicon Configuration: Settings for favicon detection and validation
"""

CONFIG = {
    # Output and Processing
    'OUTPUT_SIZE': 512,  # Target size (width and height) in pixels for all processed logos
    'MIN_SOURCE_SIZE': 120,  # Minimum source image dimension in pixels to avoid quality loss
    'BATCH_SIZE': 200,  # Number of companies to process in each parallel batch
    'OUTPUT_FOLDER': 'logos',  # Directory where processed logos are saved
    'TEMP_FOLDER': 'temp',  # Directory for temporary files during processing
    'INPUT_FILE': 'Companies.xlsx',  # Excel file containing company data
    'CORNER_RADIUS': 40,  # Corner radius in pixels for default logo rounded rectangles

    # Service Rate Limits (requests per minute)
    'CLEARBIT_RATE_LIMIT': 3600,  # 60 requests per second for Clearbit API
    'DUCKDUCKGO_RATE_LIMIT': 1800,  # 30 requests per second for DuckDuckGo service
    'FAVICON_RATE_LIMIT': 1800,  # 30 requests per second for favicon fetching

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,  # Timeout in seconds for HTTP requests
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  # User agent for HTTP requests

    # Favicon Service Configuration
    'FAVICON_MIN_SIZE': 32,  # Minimum acceptable favicon size in pixels
    'FAVICON_LOCATIONS': [  # Paths to check for favicons on company domains
        '/favicon.ico',  # Standard favicon location
        '/favicon.png',  # PNG favicon alternative
        '/apple-touch-icon.png',  # iOS/macOS touch icon
        '/apple-touch-icon-precomposed.png',  # Legacy iOS touch icon
        '/apple-touch-icon-180x180.png',  # High-res Apple touch icon
        '/apple-touch-icon-152x152.png',  # iPad touch icon
        '/apple-touch-icon-144x144.png',  # Legacy high-res icon
        '/apple-touch-icon-120x120.png',  # iPhone Retina icon
        '/apple-touch-icon-114x114.png',  # Legacy iPhone Retina
        '/apple-touch-icon-76x76.png',    # iPad mini icon
        '/apple-touch-icon-72x72.png',    # Legacy iPad icon
        '/apple-touch-icon-60x60.png',    # iPhone icon
        '/mstile-144x144.png',           # Windows 8/10 tile icon
        '/mstile-150x150.png',           # Windows 8/10 tile icon
        '/android-chrome-192x192.png',    # Android home screen icon
        '/android-chrome-512x512.png',    # Android splash screen icon
        '/site.webmanifest',             # Web app manifest (may contain icon paths)
        '/browserconfig.xml'              # IE11/Edge configuration file
    ]
}