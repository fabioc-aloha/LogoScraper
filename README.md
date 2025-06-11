![Company Logo Scraper Banner](banner.png)

# Company Logo Scraper

A robust Python utility for downloading, standardizing, and tracking company logos from various sources. The tool supports batch processing, progress tracking, resumable operation, and enriched data export, making it suitable for large-scale, reliable logo collection.

## Key Features

- Downloads company logos from multiple sources (Clearbit, favicon, or generates default logos)
- Batch processing with configurable size and parallelism
- Progress tracking and resume capability (avoids reprocessing completed/failed companies)
- Command-line interface for flexible configuration
- Filtering by specific IDs
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
- `--max-processes`, `-p`: Maximum parallel processes (overrides config)
- `--filter`, `-f`: Filter data (format: "column=value")
- `--id`: Process only the specified ID(s) (can be used multiple times)
- `--clean`, `-c`: Clean temporary files before starting

Run `python main.py --help` for a full list and details.

> **Note:** CLI arguments always override defaults in `src/config.py`. For permanent changes, edit `src/config.py` directly.

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
python main.py --input "input/Companies.xlsx" --output "logos" --batch-size 100 --max-processes 8 --id 12345 --clean
```

## See Also
- `DECISIONS.md` for architectural decisions
- `LEARNINGS.md` for project learnings and notes
- `config.py` for configuration options

## 📊 Codebase & Processing Flow

For a visual overview and detailed process pipeline, see [`flow.md`](./flow.md). This document includes:
- High-level architecture diagrams
- Step-by-step processing flow
- Service and error handling diagrams
- Key supporting modules and data flow

This is recommended for new contributors and anyone seeking to understand the end-to-end logic of the Company Logo Scraper.

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
- **Real-time ETA estimation** for large datasets
- Handles failures gracefully with detailed logging
- Supports filtering by country, ID, or custom criteria
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

### 1. Prepare the Python Environment (Recommended)

For Windows/PowerShell users, use the provided batch file for a fully automated setup:

```powershell
./prepare_env.bat
```

This will:
- Create a virtual environment (if needed)
- Activate it
- Upgrade pip
- Install all dependencies (including dev tools) from `pyproject.toml`

*If you prefer manual setup, see below for pip/venv instructions.*

### 2. Prepare your data:
- Excel file with columns: `ID`, `CompanyName`, `WebsiteURL` (optional), `Country` (optional)

### 3. Run the scraper:
```powershell
python main.py --input "path/to/Companies.xlsx" --output "path/to/logos"
```

### 4. Need help?
```powershell
python main.py --help
```

## 📋 Common Examples

```bash
# Basic usage with custom paths
python main.py --input "C:\\Data\\Companies.xlsx" --output "C:\\Data\\logos"

# Filter by country and process specific companies
python main.py --filter "Country=US" --id 12345 --id 67890

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
| `--id` | Process specific company IDs | None |
| `--clean`, `-c` | Clear temp files before starting | False |

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

## 🗂️ Project Structure

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
└── logo/                  # 🖼️ Downloaded logos saved here    ├── 12345.png          # Logo files named by ID
    ├── 67890.png
    └── ...
```

> **💡 Note:** These paths are defaults and can be overridden using command-line arguments (`--input`, `--output`) or by editing `src/config.py`.

## 📝 Documentation

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