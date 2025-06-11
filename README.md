![Company Logo Scraper Banner](banner.png)

# Company Logo Scraper

A modern Python tool for automating the download and standardization of company logos at scale. Perfect for CRM systems, business directories, and any workflow needing consistent branding assets.

**Why choose Company Logo Scraper?**
- **Save hours of manual work:** Instantly collect hundreds or thousands of company logos with a single command.
- **Boost your data quality:** Ensure every company record has a high-quality, standardized logo for a professional look in your apps, reports, or websites.
- **Seamless integration:** Designed for easy use in data pipelines, ETL jobs, and business automation scripts.
- **No more duplicates or missed companies:** The tool automatically skips already-processed companies and resumes where it left off.
- **Flexible and future-proof:** Works with any Excel data, supports new logo sources, and is easy to extend.
- **Open source and community-driven:** Actively maintained, well-documented, and ready for your contributions.

---

## Why Use This Tool?
- **Automated, multi-source logo collection** (Clearbit, favicon, or text-based fallback)
- **Batch and parallel processing** for speed
- **Resumable and reliable**: never duplicate work—existing logo files are detected automatically
- **Flexible CLI**: filter, target, and tune performance with intuitive options
- **Multilingual support**: works with company names in any language
- **Simple setup**: one command to get started

---

## 🚀 Quick Start
1. **Set up your environment:**
   ```powershell
   ./prepare_env.bat
   ```
   This creates a virtual environment and installs all dependencies from `pyproject.toml`.
2. **Prepare your data:**
   - Excel file with columns: `ID`, `CompanyName`, `WebsiteURL` (optional), `Country` (optional)
3. **Run the scraper:**
   ```powershell
   python main.py --input "Companies.xlsx" --output "logos"
   ```
4. **Need help?**
   ```powershell
   python main.py --help
   ```

---

## Usage Examples
```bash
# Filter by country and process specific companies
python main.py --filter "Country=US" --id 12345 --batch-size 150 --max-processes 4

# Process only a subset of companies by ID
python main.py --id 12345 --id 67890

# Change batch size and parallelism
python main.py --batch-size 200 --max-processes 8
```

---

## Configuration
- Edit `src/config.py` for permanent defaults (logo size, batch size, etc.)
- CLI arguments always override config file values for a single run

---

## How It Works
1. **Reads your Excel file** and loads company data
2. **Filters companies** based on CLI options (IDs, country, etc.)
3. **Checks output folder** for existing logo files and skips already-processed companies
4. **Downloads logos** from multiple sources (Clearbit, favicon, or generates a fallback)
5. **Standardizes images** to consistent PNG format and size
6. **Saves results** to the output folder and updates progress
7. **Handles errors** gracefully and continues processing

---

## Project Structure
```
LogoScraper/
├── main.py                 # Main entry point
├── src/                    # Core application code
├── tests/                  # Test suite
├── temp/                   # Temporary files (auto-managed)
├── example_companies.csv   # Sample data
├── ... (docs)
```

---

## Documentation
- [GETTING_STARTED.md](GETTING_STARTED.md): Setup and onboarding
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md): Common issues and solutions
- [CONTRIBUTING.md](CONTRIBUTING.md): How to contribute
- [DECISIONS.md](DECISIONS.md): Architecture & design
- [LEARNINGS.md](LEARNINGS.md): Project insights
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md): Release process

---

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, testing, and submitting pull requests.

## License
MIT License - See [LICENSE](LICENSE)

---

See [CHANGELOG.md](CHANGELOG.md) for release history and technical changes.