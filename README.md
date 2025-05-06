# Company Logo Scraper

A high-performance Python utility that automatically downloads and standardizes company logos from various sources. Uses parallel processing and intelligent caching to achieve optimal performance while maintaining high success rates through multiple fallback mechanisms.

## Key Features

### Performance and Optimization
- Parallel processing using Python's multiprocessing
- Resource-efficient operation with automatic CPU core management
- Intelligent caching of failed domains to prevent redundant requests
- Session reuse for optimal network performance
- Memory-efficient batch processing
- Proper resource cleanup and memory management

### Logo Sources (In Order of Priority)
1. Clearbit Logo API (Primary source)
2. DuckDuckGo Icons Service (First fallback)
3. Default Logo Generation (Final fallback)

### Image Processing
- Standardizes logos to configurable dimensions
- Maintains aspect ratios with centered positioning
- Handles transparency with white background
- Supports ICO and various image formats
- High-quality scaling using Lanczos resampling
- Image validation and verification
- Quality control:
  - Minimum size requirements
  - Maximum upscaling ratio of 8x
  - Format validation and conversion

### Smart URL Handling
- Multiple URL fallbacks per company
- Automatic scheme detection (http/https)
- Malformed URL cleanup
- International domain support
- Email-style URL cleanup
- Domain extraction and normalization

### Default Logo Generator
- Professional color schemes
- Dynamic text sizing and layout
- Multi-language support (CJK + Latin)
- Multiple font fallbacks
- Automatic text arrangement for long names
- Visual weight compensation
- Consistent branding elements

### Process Management
- Configurable parallel batch processing
- Built-in rate limiting for APIs
- Progress tracking with auto-resume
- Comprehensive logging system
- Error recovery and retry mechanisms
- Proper resource cleanup
- Memory usage optimization

## Requirements

Install required packages via pip:
```bash
pip install -r requirements.txt
```

Dependencies:
- requests==2.31.0: HTTP request handling
- pandas==2.1.4: Data processing
- Pillow==10.1.0: Image processing
- openpyxl==3.1.2: Excel file support
- ratelimit==2.2.1: API rate limiting
- urllib3==2.1.0: Enhanced HTTP support
- Additional dependencies for full functionality listed in requirements.txt

## Configuration

All settings are centralized in `config.py`:

### Core Settings
- `OUTPUT_SIZE`: Logo dimensions (default: 512×512)
- `MIN_SOURCE_SIZE`: Minimum source image size (default: 120px)
- `BATCH_SIZE`: Parallel processing batch size (default: 200)
- `OUTPUT_FOLDER`: Logo storage location
- `TEMP_FOLDER`: Temporary processing directory
- `INPUT_FILE`: Source Excel file name
- `CORNER_RADIUS`: Default logo corner rounding

### Service Configuration
Rate limits (per minute):
- Clearbit API: 3600 (60/sec)
- DuckDuckGo: 1800 (30/sec)

### Network Settings
- `REQUEST_TIMEOUT`: HTTP timeout (default: 10s)
- `USER_AGENT`: Browser identification string

## Project Structure

```
├── logo_scraper.py           # Main application entry point
├── services/                 # Logo service implementations
│   ├── clearbit_service.py   # Clearbit API integration
│   ├── duckduckgo_service.py # DuckDuckGo service
│   └── default_service.py    # Default logo generator
├── utils/                    # Utility modules
│   ├── batch_processor.py    # Parallel batch processing
│   ├── company_processor.py  # Individual company processing
│   ├── filter_utils.py       # DataFrame filtering
│   ├── url_utils.py          # URL processing
│   ├── image_utils.py        # Image processing
│   └── progress_tracker.py   # Progress management
├── logos/                    # Processed logos
├── temp/                     # Temporary files
├── Companies.xlsx            # Input data
└── requirements.txt          # Python dependencies
```

## Input File Format

The script expects an Excel file (`Companies.xlsx`) with these columns:

Required Fields:
- `TPID`: Unique company identifier (used for filename)
- `TPAccountName`: Primary company name
- `CRMAccountName`: Alternative company name (fallback)
- `WebsiteURL`: Primary website URL
- `WebsiteURLspm`: Backup website URL

Data Handling:
- Company names: Tries TPAccountName first, falls back to CRMAccountName
- URLs: Checks WebsiteURL first, falls back to WebsiteURLspm
- Generates default logo if no online logo found

## Usage

1. Prepare your environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Unix/MacOS
   pip install -r requirements.txt
   ```

2. Place your Companies.xlsx file in the project directory

3. Run the script:
   ```bash
   python logo_scraper.py
   ```

The script will:
- Process companies in parallel batches
- Respect API rate limits
- Save logos as standardized PNGs
- Track progress for resume capability
- Provide detailed logging

## Output

- Standardized logos in `logos/{TPID}.png`
- Progress tracking in `download_progress.json`
- Detailed logs in `logo_scraper.log`
- Failed domain cache for optimization

## Performance Optimization

The script includes several optimizations:
1. Parallel processing using multiple CPU cores
2. Failed domain caching to avoid redundant requests
3. Session reuse for network efficiency
4. Unordered processing for maximum throughput
5. Efficient resource cleanup
6. Memory usage management
7. Configurable batch sizes

## Error Handling

Comprehensive error handling for:
- Network failures
- API rate limits
- Invalid image data
- Resource constraints
- File system issues
- Data validation
- Memory management

## Resource Management

The script properly manages:
- Network connections
- Temporary files
- Memory usage
- CPU utilization
- API rate limits
- File handles

## Logging

Detailed logging includes:
- Operation timestamps
- Success/failure tracking
- Processing statistics
- Error details
- Resource usage
- Performance metrics
- Batch processing status