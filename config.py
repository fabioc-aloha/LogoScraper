"""Global configuration for the logo scraper"""

CONFIG = {
    # Output and Processing
    'OUTPUT_SIZE': 512,  # Target size for logos
    'MIN_SOURCE_SIZE': 120,  # Minimum source image size to avoid excessive upscaling
    'BATCH_SIZE': 200,  # Number of companies to process in each batch
    'OUTPUT_FOLDER': 'logos',  # Output folder for saved logos
    'TEMP_FOLDER': 'temp',  # Temporary folder for logo validation
    'INPUT_FILE': 'Companies.xlsx',  # Input Excel file containing company data
    'CORNER_RADIUS': 40,  # Corner radius for rounded rectangles in default logos

    # Service Rate Limits (requests per minute)
    'CLEARBIT_RATE_LIMIT': 3600,  # 60 requests per second
    'DUCKDUCKGO_RATE_LIMIT': 1800,  # 30 requests per second
    'FAVICON_RATE_LIMIT': 1800,  # 30 requests per second

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,  # Timeout for HTTP requests in seconds
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',

    # Favicon Service Configuration
    'FAVICON_MIN_SIZE': 32,  # Minimum size for favicons in pixels
    'FAVICON_LOCATIONS': [  # Common favicon locations to check
        '/favicon.ico',
        '/favicon.png',
        '/apple-touch-icon.png',
        '/apple-touch-icon-precomposed.png',
        '/apple-touch-icon-180x180.png',  # High-res Apple touch icon
        '/apple-touch-icon-152x152.png',  # iPad touch icon
        '/apple-touch-icon-144x144.png',  # Legacy high-res
        '/apple-touch-icon-120x120.png',  # iPhone Retina
        '/apple-touch-icon-114x114.png',  # Legacy iPhone Retina
        '/apple-touch-icon-76x76.png',    # iPad mini
        '/apple-touch-icon-72x72.png',    # Legacy iPad
        '/apple-touch-icon-60x60.png',    # iPhone
        '/mstile-144x144.png',           # Windows 8/10 tile
        '/mstile-150x150.png',           # Windows 8/10 tile
        '/android-chrome-192x192.png',    # Android home screen
        '/android-chrome-512x512.png',    # Android splash screen
        '/site.webmanifest',             # Web manifest may contain icon paths
        '/browserconfig.xml'              # IE11/Edge configuration file
    ]
}