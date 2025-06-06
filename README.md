![Company Logo Scraper Banner](banner.png)

# Company Logo Scraper

A robust Python utility for downloading, standardizing, and tracking company logos from various sources. The tool supports batch processing, progress tracking, resumable operation, and enriched data export, making it suitable for large-scale, reliable logo collection.

## Key Features

- Downloads company logos from multiple sources (Clearbit, favicon, or generates default logos)
- Batch processing with configurable size and parallelism
- Progress tracking and resume capability (avoids reprocessing completed/failed companies)
- Command-line interface for flexible configuration
- Filtering by specific TPIDs
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

**Minimum Acceptable Logo Size:** Logos must now be at least **24x24 pixels** by default (configurable). Images smaller than this will be rejected as too low quality.

This ensures that only truly invalid domains are skipped, improving logo fetch rates and reducing errors.

## Logo Size Requirements
- The minimum source size for logos is controlled by the `MIN_SOURCE_SIZE` setting in `config.py` (default: 24).
- **At least one dimension (width or height) must be greater than or equal to `MIN_SOURCE_SIZE`.**
- Images where both dimensions are below this threshold are rejected as too small.
- You can change this minimum in `config.py` as needed.

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
python logo_scraper.py --input "input/Companies.xlsx" --output "logos" --batch-size 100 --max-processes 8 --tpid 12345 --top 50 --clean
```

## See Also
- `DECISIONS.md` for architectural decisions
- `LEARNINGS.md` for project learnings and notes
- `config.py` for configuration options

---
>>>>>>> origin/master

# Company Logo Scraper

🚀 **Automatically download and standardize company logos at scale**

Perfect for CRM systems, business directories, or any application needing consistent company branding assets.

## ✨ Features
- Downloads logos from multiple sources (Clearbit API, favicons, or generates text-based defaults)
- Standardizes to consistent 256×256 PNG files
- Processes in batches with parallel processing for speed
- Tracks progress and resumes if interrupted
- Handles failures gracefully with detailed logging
- Supports filtering by country, TPID, or custom criteria
- Works globally with multilingual company names

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
>>>>>>> origin/master

## 🚀 Quick Start

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

## 🚀 Quick Start

1. **Install dependencies:**
- pandas: Data processing
- Pillow: Image processing
- openpyxl: Excel file support
- ratelimit: API rate limiting

## Configuration

Configuration is centralized in `config.py` for simplicity:

### Core Settings
- `OUTPUT_SIZE`: Logo dimensions (default: 256×256, configurable)
- `MIN_SOURCE_SIZE`: Minimum source image size (default: 24px, configurable)
- `BATCH_SIZE`: Parallel processing batch size (default: 300, configurable)
- `MAX_RETRIES`: Maximum number of retry attempts (default: 3, configurable)
- `RETRY_DELAY`: Base delay between retries in seconds (default: 1.0, configurable)

### Service Settings
- Rate limits and timeouts
- API endpoints
- HTTP configurations
- Search parameters

## Directory Structure

```
C:\Data\                   # Base data directory
    ├── logo\              # Processed company logos
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
>>>>>>> origin/master
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your data:**
   - Excel file with columns: `tpid`, `crmaccountname`, `websiteurl` (optional), `country` (optional)

3. **Run the scraper:**
   ```bash
   python main.py --input "path/to/Companies.xlsx" --output "path/to/logos"
   ```

4. **Need help?**
   ```bash
   python main.py --help
   ```

## 📋 Common Examples

```bash
# Basic usage with custom paths
python main.py --input "C:\\Data\\Companies.xlsx" --output "C:\\Data\\logos"

# Filter by country and process specific companies
python main.py --filter "country=US" --tpid 12345 --tpid 67890

# Adjust performance settings
python main.py --batch-size 150 --max-processes 4

# Clean temporary files and start fresh
python main.py --clean

# Debug mode with detailed logging
python main.py --log-level DEBUG

# Process only the first 50 companies
python logo_scraper.py --top 50

# Clean temporary files automatically
python logo_scraper.py --clean

# Set logging level
python logo_scraper.py --log-level DEBUG
```

## ⚙️ Key Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Path to your Excel file | See config.py |
| `--output`, `-o` | Where to save logos | See config.py |
| `--batch-size`, `-b` | Companies per batch | 300 |
| `--max-processes`, `-p` | Parallel workers | 8 |
| `--filter`, `-f` | Filter data (format: "column=value") | None |
| `--tpid` | Process specific company IDs | None |
| `--clean`, `-c` | Clear temp files before starting | False |
| `--log-level`, `-l` | Logging detail (DEBUG, INFO, ERROR) | INFO |

### Output Files
- PNG logos in `C:\Data\logo\{TPID}.png` (default output folder, configurable in `config.py`)
- Processing logs in `logo_scraper.log`
- Progress tracking in `download_progress.json`
- Enriched data Excel file with results

> **💡 Pro Tip:** CLI arguments override defaults in `src/config.py`

## 🛠️ Configuration

For permanent changes, edit `src/config.py`:

**Essential settings:**
- `OUTPUT_SIZE`: Logo size in pixels (default: 256)
- `BATCH_SIZE`: Companies per batch (default: 300)
- `MAX_PROCESSES`: Parallel workers (default: 8)
- `INPUT_FILE`: Default Excel file path
- `OUTPUT_FOLDER`: Default logo save location

> **Tip:** Use CLI arguments for one-time changes, edit config.py for permanent defaults.

## 📤 What You Get

- **Logos**: 256×256 PNG files saved as `{TPID}.png` in your output directory
- **Processing logs**: Detailed progress and error information in `logo_scraper.log`
- **Progress tracking**: Resume interrupted runs with `download_progress.json`
- **Enriched data**: Updated Excel file with processing results and logo sources (timestamped)

## 🔄 Smart Features

- **Resumable**: Automatically resumes interrupted processing
- **Self-cleaning**: Use `--clean` to start fresh or follow prompts for leftover temp files
- **Domain cleaning**: Intelligently extracts domains from complex website fields
- **Multilingual**: Handles company names in any language with appropriate fonts
- **Error recovery**: Graceful handling of failed downloads with detailed logging

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test with details
pytest tests/test_logo_scraper_core.py -v
```

## 📂 Project Structure

```
LogoScraper/
├── main.py                 # 🎯 Main entry point (run this!)
├── requirements.txt        # 📦 Dependencies
├── example_companies.csv   # 📋 Sample data file to get started
├── src/                   # 🔧 Core application code
│   ├── config.py          # ⚙️ Configuration settings
│   ├── logo_scraper_core.py # 🎨 Main scraping logic
│   ├── services/          # 🌐 External API integrations
│   └── utils/             # 🛠️ Helper utilities
├── tests/                 # 🧪 Test suite
├── temp/                  # 📁 Temporary files & logs
└── docs/                  # 📚 Documentation
    ├── GETTING_STARTED.md # 🚀 Beginner's guide
    ├── TROUBLESHOOTING.md # 🔧 Common issues & solutions
    ├── DECISIONS.md       # 🏗️ Architecture decisions
    ├── LEARNINGS.md       # 📝 Development insights
    └── RELEASE_CHECKLIST.md # ✅ Release process
```

### 📁 Default Data Folder Structure

The application expects the following data folder structure (configurable in `src/config.py`):

```
C:\Data/
├── input/
│   └── Companies.xlsx      # 📊 Your company data (default location)
└── logo/                  # 🖼️ Downloaded logos saved here
    ├── 12345.png          # Logo files named by TPID
    ├── 67890.png
    └── ...
```

> **💡 Note:** These paths are defaults and can be overridden using command-line arguments (`--input`, `--output`) or by editing `src/config.py`.

## 📚 Documentation

- **New to this tool?** Start with [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- **Having issues?** Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick contributing steps:**
- Review [docs/DECISIONS.md](docs/DECISIONS.md) for architectural principles
- Follow existing code style and patterns  
- Add tests for new features
- Update documentation as needed

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

**Made with ❤️ by [Fabio Correa](mailto:fabio@correax.com)**