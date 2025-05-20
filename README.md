# Company Logo Scraper

A robust Python utility for downloading, standardizing, and tracking company logos from various sources. The tool supports batch processing, progress tracking, resumable operation, and enriched data export, making it suitable for large-scale, reliable logo collection.

## Key Features

- Downloads company logos from multiple sources (Clearbit, favicon, or generates default logos)
- Batch processing with configurable size and parallelism
- Progress tracking and resume capability (avoids reprocessing completed/failed companies)
- Command-line interface for flexible configuration
- Filtering by column values or specific TPIDs
- Enriched data export with logo source statistics
- Detailed logging and error handling
- Temporary file management and cleaning
- Multilingual support for company names

## Domain Cleaning Logic
The logo scraper uses a robust domain cleaning function to maximize the number of valid domains processed:
- Removes anything after '@' (e.g., user@domain.com → domain.com)
- Splits on common delimiters (commas, semicolons, slashes, backslashes, whitespace, etc.) and uses only the first valid part
- Removes unwanted characters: quotes, angle brackets, parentheses, brackets, etc.
- Strips common prefixes like `www.`
- Removes leading/trailing dots and hyphens
- Handles multiple domains in a single field, using only the first valid one

**Minimum Acceptable Logo Size:** Logos must now be at least **28x28 pixels**. Images smaller than this will be rejected as too low quality.

This ensures that only truly invalid domains are skipped, improving logo fetch rates and reducing errors.

## Logo Size Requirements
- The minimum source size for logos is controlled by the `MIN_SOURCE_SIZE` setting in `config.py`.
- **At least one dimension (width or height) must be greater than or equal to `MIN_SOURCE_SIZE`.**
- Images where both dimensions are below this threshold are rejected as too small.

## Upscaling Behavior
- There is no longer a maximum upscaling ratio. Any image meeting the minimum size requirement will be upscaled to the configured output size (`OUTPUT_SIZE`).
- This allows for visual inspection of small favicons and other low-resolution images.

## Diagnostics & Logging
- All logo fetch failures (especially from Clearbit) are logged with HTTP status codes and response content for easier troubleshooting.
- The log file (`logo_scraper.log`) provides detailed progress, error, and summary information for each run.

## Workflow Overview

1. **Parse command-line arguments** and update configuration.
2. **Optionally clean** temporary files before starting.
3. **Initialize** the LogoScraper, validate configuration, and set up logging.
4. **Load and filter input data**, excluding already processed companies.
5. **Process companies in batches**, updating progress and saving enriched results.
6. **Export enriched data** to a timestamped Excel file with summary statistics.
7. **On completion or interruption**, save state and output summary statistics.

## Command-Line Arguments

- `--input`, `-i`: Path to the input Excel file (overrides config)
- `--output`, `-o`: Output directory for logos (overrides config)
- `--temp`, `-t`: Temporary directory for processing (overrides config)
- `--batch-size`, `-b`: Number of companies per batch (overrides config)
- `--log-level`, `-l`: Logging level (DEBUG, INFO, etc.)
- `--max-processes`, `-p`: Maximum parallel processes (overrides config)
- `--top`, `-n`: Process only the first N companies
- `--clean`, `-c`: Clean temporary files before starting
- `--filter`, `-f`: Add a filter in format "column=value" (can be used multiple times)
- `--tpid`: Process only the specified TPID(s) (can be used multiple times)

Run `python logo_scraper.py --help` for a full list and details.

## Outputs

- PNG logos in the output directory (e.g., `logos/{TPID}.png`)
- Processing logs in `logo_scraper.log`
- Progress tracking in `download_progress.json`
- Enriched data Excel file with results and logo source summary (timestamped)

## Resumable Operation & Cleaning

- The script tracks completed and failed companies, so interrupted runs can be resumed without duplicating work.
- Use `--clean` to clear temporary files before starting a new run.
- The script will prompt to clean temp files if leftovers are detected.

## Example Usage

```bash
python logo_scraper.py --input "input/Companies.xlsx" --output "logos" --batch-size 100 --max-processes 8 --filter "country=US" --tpid 12345 --clean
```

## See Also
- `DECISIONS.md` for architectural decisions
- `LEARNINGS.md` for project learnings and notes
- `config.py` for configuration options

---

# Company Logo Scraper

A streamlined Python utility that downloads and standardizes company logos from various sources, with built-in fallbacks and parallel processing capabilities.

## Key Features

### Core Functionality
- Downloads company logos from Clearbit API (primary source)
- Falls back to domain favicons via DuckDuckGo and Google S2 if Clearbit fails
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
- `OUTPUT_SIZE`: Logo dimensions (default: 256×256)
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
├── logo_scraper.py        # Main entry point and orchestrator
├── config.py              # Centralized configuration (all settings)
├── DECISIONS.md           # Architectural decisions and rationale
├── LEARNINGS.md           # Project learnings, technical notes, and best practices
├── README.md              # Usage guide and documentation
├── requirements.txt       # Python dependencies
├── LICENSE                # Project license
├── services/              # Integrations for logo sources (Clearbit, favicon, default)
├── utils/                 # Internal utilities (batching, progress, image, text, etc.)
├── temp/                  # Temporary files, logs, and progress tracking (auto-created)
└── tests/                 # Unit and integration tests
```

## Architecture Overview

The project is organized for clarity, modularity, and extensibility:

- **logo_scraper.py**: Main script. Handles argument parsing, configuration, batch processing, progress tracking, and orchestration of the entire workflow.
- **config.py**: All configuration options (paths, batch size, logo size, API settings, etc.) are centralized here for easy management.
- **services/**: Contains service modules for fetching/generating logos:
  - `clearbit_service.py`: Fetches logos from the Clearbit API
  - `favicon_service.py`: Fetches favicons using DuckDuckGo and Google S2 as fallback sources (no direct site scraping)
  - `default_service.py`: Generates default logos when no online logo is available
- **utils/**: Utility modules for:
  - Progress tracking (`progress_tracker.py`)
  - Batch processing (`batch_processor.py`)
  - Image and text processing (`image_resizer.py`, `text_renderer.py`, etc.)
  - Domain and URL cleaning (`url_utils.py`, `domain_filter.py`)
  - Logging, config validation, and more
- **tests/**: Comprehensive test suite for all major components and integration scenarios
- **temp/**: Stores logs, progress files, and temporary data (auto-created and safe to delete)

This structure supports robust, large-scale logo scraping with clear separation of concerns and easy extensibility.

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

## Testing

The project includes a comprehensive test suite to ensure reliability and correctness. Tests are organized in the `tests/` directory and cover both individual components and integration scenarios.

### Running Tests

To run the full test suite:

```bash
python -m unittest discover -s tests
```

To run specific test files:

```bash
python -m unittest tests.test_input_service
python -m unittest tests.test_specific_logos
```

### Test Coverage

The test suite covers the following key components:

1. **Input Data Service Tests** (`test_input_service.py`)
   - Data filtering and validation
   - Excel file loading
   - Column name normalization
   - Error handling for malformed data

2. **Logo Generation Tests** (`test_specific_logos.py`)
   - End-to-end logo generation workflow
   - Testing specific challenging company names
   - Multilingual text rendering
   - Image quality verification

### Adding New Tests

When adding new functionality, include appropriate tests that verify:
- Correct behavior under normal conditions
- Proper error handling for edge cases
- Performance meets expectations for large-scale processing

Tests should be isolated and not depend on external services when possible. Mock the external services for unit tests to avoid network dependencies.

## Contributing

When contributing to this project:

1. Review the `DECISIONS.md` file to understand the architectural principles
2. Follow the existing code style and patterns
3. Add appropriate documentation for new features
4. Include unit tests for new functionality
5. Update the `README.md` and `DECISIONS.md` as needed

## License

MIT License - See LICENSE file for details