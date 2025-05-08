# Company Logo Scraper

A streamlined Python utility that downloads and standardizes company logos from various sources, with built-in fallbacks and parallel processing capabilities.

## Key Features

### Core Functionality
- Downloads company logos from Clearbit API (primary source)
- Falls back to domain favicons via DuckDuckGo icons service (`.ico`) if Clearbit fails
- Generates default logos when online logos unavailable (draws square backgrounds without rounded corners, uses up to 4-character initials)
- Standardizes all logos to consistent format and size
- Parallel processing for efficiency
- Progress tracking and resume capability
- Comprehensive multilingual support for all languages and scripts
- Robust HTTP retry logic with exponential backoff
- Command-line interface for easier configuration

### Image Processing
- Standardizes logos to configurable dimensions
- Maintains aspect ratios
- Handles transparency
- Basic quality controls
- Improved text rendering for international characters
- Better vertical positioning of text in generated logos
- Draws square backgrounds for default logos (no rounded corners)

### URL Handling
- URL cleanup and normalization
- Domain filtering and validation
- Search result caching

### Process Management
- Parallel processing with configurable workers
- Comprehensive progress tracking
- Enhanced error handling and logging
- Resource cleanup
- Detailed real-time progress reporting
- Estimated time remaining calculations
- Source breakdown statistics

## Requirements

Install required packages via pip:
```bash
pip install -r requirements.txt
```

Core Dependencies:
- requests: HTTP request handling
- pandas: Data processing
- Pillow: Image processing
- openpyxl: Excel file support
- ratelimit: API rate limiting

## Configuration

Configuration is centralized in `config.py` for simplicity:

### Core Settings
- `OUTPUT_SIZE`: Logo dimensions (default: 512×512)
- `MIN_SOURCE_SIZE`: Minimum source image size (default: 60px)
- `BATCH_SIZE`: Parallel processing batch size (default: 300)
- `MAX_RETRIES`: Maximum number of retry attempts (default: 3)
- `RETRY_DELAY`: Base delay between retries in seconds (default: 1.0)

### Service Settings
- Rate limits and timeouts
- API endpoints
- HTTP configurations
- Search parameters

## Directory Structure

```
C:\Data\                    # Base data directory
    ├── logos\             # Processed company logos
    ├── temp\              # Temporary processing files
    └── input\             # Input Excel files

Project Structure:
├── logo_scraper.py        # Main entry point
├── config.py              # Centralized configuration
├── DECISIONS.md           # Architectural decisions documentation
├── README.md              # This usage guide
├── services/              # External service integrations
└── utils/                 # Internal utilities
```

## Input Format

Required Excel file fields:
- `tpid`: Unique identifier
- `crmaccountname`: Company name
- `websiteurl`: Optional website URL
- `country`: Optional, used for URL discovery

## Usage

1. Setup environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Prepare directories:
   ```bash
   mkdir "C:\Data\input" "C:\Data\logos" "C:\Data\temp"
   ```

3. Add Companies.xlsx to C:\Data\input

4. Run:
   ```bash
   python logo_scraper.py
   ```

### Command Line Options

```bash
# Display help
python logo_scraper.py --help

# Process only specific TPIDs
python logo_scraper.py --tpid 54491231 --tpid 1112118

# Use custom input/output paths
python logo_scraper.py --input "path/to/input.xlsx" --output "path/to/logos"

# Set batch size and max processes
python logo_scraper.py --batch-size 100 --max-processes 12

# Process only the first 50 companies
python logo_scraper.py --top 50

# Apply filters
python logo_scraper.py --filter "country=US" --filter "industry=Technology"

# Clean temporary files automatically
python logo_scraper.py --clean

# Set logging level
python logo_scraper.py --log-level DEBUG
```

## Outputs

- PNG logos in `C:\Data\logos\{TPID}.png`
- Processing logs in `logo_scraper.log`
- Progress tracking in `download_progress.json`
- Enriched data Excel file with results

## Error Handling

- Graceful fallbacks for failed logo downloads
- Progress preservation on interruption
- Comprehensive logging
- Input validation
- HTTP retry mechanism with exponential backoff
- Better error reporting and tracking

## Multilingual Support

The application provides comprehensive support for company names in all languages:

- Full support for non-Latin scripts (CJK, Cyrillic, Arabic, etc.)
- Special handling for Turkish, Korean, and other challenging scripts
- Automatic script detection to optimize font selection
- Fallback mechanisms for rare character sets
- Appropriate font selection for each language

## Project Philosophy

The project follows these key principles:
1. Simplicity over complexity
2. Appropriate separation of concerns
3. Clear error handling and logging
4. Consistent configuration
5. Balanced module organization

## Architecture Documentation

This project includes a `DECISIONS.md` file that documents the architectural decisions made during development. This file explains:

1. **Purpose and Goals** - The overall objectives of the project
2. **Architectural Decisions** - Detailed explanations of key design choices
3. **Implementation Details** - How each component was implemented
4. **Pending Improvements** - Areas identified for future enhancement

The `DECISIONS.md` file serves as both documentation for new contributors and as a record of the reasoning behind important design choices. If you're planning to extend or modify the code, reviewing this file is highly recommended.

## Contributing

When contributing to this project:

1. Review the `DECISIONS.md` file to understand the architectural principles
2. Follow the existing code style and patterns
3. Add appropriate documentation for new features
4. Include unit tests for new functionality
5. Update the `README.md` and `DECISIONS.md` as needed

## License

MIT License - See LICENSE file for details