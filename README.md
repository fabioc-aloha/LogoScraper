![Company Logo Scraper Banner](banner.png)

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

## 🚀 Quick Start

1. **Install dependencies:**
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