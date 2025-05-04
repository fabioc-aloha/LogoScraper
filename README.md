# Company Logo Scraper

A Python utility that automatically downloads company logos from various sources and standardizes them into a consistent PNG format. Achieves a high success rate through multiple fallback mechanisms and robust error handling.

## Features

- Fetches logos from multiple sources in order of preference:
  1. Clearbit Logo API
  2. DuckDuckGo Icons Service (fallback)
  3. Default logo generation as final fallback

- Image Processing:
  - Standardizes all logos to configured dimensions
  - Maintains aspect ratios
  - Handles transparency with white background
  - Supports ICO and various image formats
  - High-quality scaling using Lanczos resampling
  - Image validation and verification
  - Configurable minimum size requirements to ensure quality
  - Maximum upscaling ratio of 8x to maintain quality

- Smart URL Handling:
  - Supports multiple URLs per company
  - Automatic scheme detection (http/https)
  - Handles malformed URLs
  - Supports international domains
  - Email-style URL cleanup
  - Multiple URL fallbacks
  - Domain extraction and normalization

- Default Logo Generation:
  - Professional color schemes
  - Company initials with proper centering
  - Multi-language support (English, Japanese, Chinese, Korean)
  - Multiple font fallbacks
  - High-quality font rendering
  - Automatic text layout for long names
  - Visual weight compensation
  - Consistent sizing and spacing

- Process Management:
  - Batch processing with configurable size (default: 200)
  - Built-in rate limiting for APIs
  - Progress tracking and resume capability
  - Comprehensive logging
  - Error recovery and retry mechanisms
  - Memory usage optimization

## Configuration

All configuration settings are centralized in `config.py`. Here's the default configuration:

```python
CONFIG = {
    'OUTPUT_SIZE': 512,      # Target size for logos (width and height in pixels)
    'MIN_SOURCE_SIZE': 120,  # Minimum source image size to avoid excessive upscaling
    'BATCH_SIZE': 200,       # Number of companies to process in each batch
    'OUTPUT_FOLDER': 'logos',# Output folder for saved logos
    'INPUT_FILE': 'Companies.xlsx',  # Input Excel file containing company data
    'CORNER_RADIUS': 40      # Corner radius for rounded rectangles in default logos
}
```

You can modify these values in `config.py` to customize the behavior of the script:
- `OUTPUT_SIZE`: Determines the final dimensions of processed logos
- `MIN_SOURCE_SIZE`: Sets the minimum acceptable source image dimensions (largest dimension must be at least this size)
- `BATCH_SIZE`: Controls how many companies are processed in each batch
- `OUTPUT_FOLDER`: Specifies where processed logos are saved
- `INPUT_FILE`: Sets the name of the input Excel file
- `CORNER_RADIUS`: Adjusts the corner roundness of generated default logos

## Project Structure

```
├── logo_scraper.py          # Main entry point
├── services/                # Logo service providers
│   ├── clearbit_service.py  # Clearbit API integration
│   ├── duckduckgo_service.py# DuckDuckGo icons service
│   └── default_service.py   # Default logo generator
├── utils/                   # Utility modules
│   ├── url_utils.py        # URL handling functions
│   ├── image_utils.py      # Image processing functions
│   └── progress_tracker.py # Progress tracking
├── logos/                  # Output directory for logos
├── Companies.xlsx          # Input file with company data
└── requirements.txt        # Python dependencies
```

## Requirements

Required packages (install via `pip install -r requirements.txt`):
- requests: For HTTP requests
- pandas: For Excel file handling
- Pillow: For image processing
- openpyxl: For Excel file support
- ratelimit: For API rate limiting
- urllib3: For enhanced HTTP support

## Setup

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix/MacOS
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Input File Format

The script expects an Excel file named `Companies.xlsx` with the following columns:
- `TPID`: Unique identifier for each company
- `CompanyName`: Company name for fallback logo generation
- `URL`: Primary website URL
- `URL1`: Alternative website URL (optional)
- `URL2`: Additional website URL (optional)

## Usage

1. Place your `Companies.xlsx` file in the project root directory
2. Run the script:
   ```
   python logo_scraper.py
   ```

The script will:
- Process companies in configurable batch sizes (default: 200)
- Automatically handle rate limits for different APIs
- Save processed logos to the `logos` folder
- Track progress in `download_progress.json`
- Initialize progress from existing logos if no progress file exists
- Log detailed information to `logo_scraper.log`

## Output

- Logos are saved in the configured output directory as `{TPID}.png`
- All logos are standardized to the configured output size in PNG format
- A progress file (`download_progress.json`) tracks completed and failed items
  - If this file is deleted, it will be recreated based on existing logos
  - Prevents reprocessing of already downloaded logos
- A log file (`logo_scraper.log`) contains detailed operation information

## Error Handling

The script includes comprehensive error handling for:
- Invalid or malformed URLs
- Failed API requests
- Invalid image data
- Network timeouts and retries
- Rate limit handling
- File system errors
- Image quality requirements:
  - Minimum size validation (largest dimension must be at least 120px)
  - Maximum upscaling ratio (8x) to maintain quality
- URL parsing errors
- Font loading failures
- Memory constraints
- API service outages

## Logging

The script provides detailed logging with:
- Timestamp for each operation
- Logo source attempts and successes
- Image processing steps and validation
- Success/failure status with reasons
- Progress statistics and success rates
- Error details and stack traces
- Batch processing statistics