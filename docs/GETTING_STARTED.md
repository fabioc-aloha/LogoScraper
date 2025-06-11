# 🚀 Getting Started Guide

**New to Company Logo Scraper?** This guide will get you up and running in 5 minutes!

## 📋 What You'll Need

Before starting, make sure you have:
- **Python 3.7 or higher** ([Download here](https://www.python.org/downloads/))
- **An Excel file** with your company data
- **Basic command line knowledge** (don't worry, we'll guide you!)

## 📊 Preparing Your Data

Your Excel file needs these columns:

| Column Name | Required? | Description | Example |
|-------------|-----------|-------------|---------|
| `ID` | ✅ Yes | Unique ID for each company | 1719150 |
| `CompanyName` | ✅ Yes | Company name | "BANCO ITAU SA" |
| `WebsiteURL` | ✅ Yes | Company website | "http://www.itau.com.br" |
| `Country` | ✅ Yes | Country name | "Brazil" |

**Example Excel structure:**
```
ID      | WebsiteURL                        | CompanyName        | Country
1719150 | http://www.itau.com.br           | BANCO ITAU SA      | Brazil
520413  | http://www.vodafone.com          | Vodafone          | United Kingdom
```

> **💡 Tip:** The scraper is smart - it can find logos even without website URLs!

## 🛠️ Step-by-Step Setup

### 1. Download and Extract
Download the Logo Scraper and extract it to a folder like `C:\LogoScraper` or `/home/user/LogoScraper`

### 2. Open Command Line
**Windows:**
- Press `Win + R`, type `cmd`, press Enter
- Navigate to your folder: `cd C:\LogoScraper`

**Mac/Linux:**
- Open Terminal
- Navigate to your folder: `cd /path/to/LogoScraper`

### 3. Prepare the Python Environment (Recommended)

Instead of manually installing requirements, use the provided batch file for a fully automated setup:

```powershell
./prepare_env.bat
```

This will:
- Create a virtual environment (if needed)
- Activate it
- Upgrade pip
- Install all dependencies (including dev tools) from `pyproject.toml`

*If you prefer manual setup, see the README for pip/venv instructions.*

### 4. Test Installation
```powershell
python main.py --help
```
*You should see a help message with all available options.*

### 5. Try with Example Data (Optional)
```powershell
python main.py --input "example_companies.csv" --output "test_logos" --batch-size 5
```
*This will test the scraper with the included sample data.*

## 🎯 Your First Run

### Simple Example
```powershell
python main.py --input "path/to/your/companies.xlsx" --output "path/to/save/logos"
```

### Try with Example Data First
```powershell
python main.py --input "example_companies.csv" --output "test_logos"
```

### Real Example (Windows)
```powershell
python main.py --input "C:\Data\Companies.xlsx" --output "C:\Data\Logos"
```

### Real Example (Mac/Linux)
```bash
python main.py --input "/Users/john/Documents/Companies.xlsx" --output "/Users/john/Documents/Logos"
```

## 🎬 What Happens Next?

1. **The scraper starts** and shows you progress
2. **It processes companies** in batches for speed
3. **Downloads logos** from various sources
4. **Saves 256×256 PNG files** named by company ID
5. **Creates a summary** when finished

## 📁 Finding Your Results

After completion, check your output folder:
```
Your Output Folder/
├── 12345.png          # Logo for company 12345
├── 67890.png          # Logo for company 67890
└── ...more logos...
```

Plus these files in the `temp/` folder:
- `logo_scraper.log` - Detailed processing log
- `Companies_enriched_[timestamp].xlsx` - Your original data with results

## 🛑 Common First-Time Issues

### "Command not found" or "python is not recognized"
**Solution:** Python isn't installed or not in your PATH
- [Download Python](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

### "No such file or directory"  
**Solution:** File path is wrong
- Use the full path to your file
- On Windows, use `\` or `/` in paths
- Make sure the file actually exists!

### "Permission denied"
**Solution:** File is locked or folder isn't writable
- Close Excel if your input file is open
- Make sure you can write to the output folder
- Try running as administrator (Windows)

## 🎛️ Useful Options for Beginners

> **Tip:** All configuration options are documented in `src/config.py`. Use CLI arguments for one-time changes, or edit `src/config.py` for permanent defaults.

### Start Small (Test with fewer companies)
```powershell
python main.py --input "file.xlsx" --output "logos" --batch-size 10
```

### Clean Start (Clear previous attempts)
```powershell
python main.py --clean --input "file.xlsx" --output "logos"
```

### See What's Happening (Debug mode)
```powershell
python main.py --input "file.xlsx" --output "logos"
# (Set logging level in config.py if needed)
```

### Filter by Country (Process only US companies)
```powershell
python main.py --filter "country=US" --input "file.xlsx" --output "logos"
```

## 🔍 Understanding the Output

### Success Messages
- `"Starting logo scraper..."` - Good start!
- `"Processing batch X of Y"` - Making progress
- 🟩 **Excellent batch** (≥90% success) - Most logos found successfully
- 🟨 **Good batch** (50-89% success) - Decent logo discovery rate
- 🟥 **Poor batch** (0-49% success) - Few or no logos found, may need troubleshooting
- `"Successfully downloaded logo"` - Found a logo!
- `"Generated text-based logo"` - Made a text logo (no image found)

### Don't Worry About These
- `"No logo found"` - Normal, not all companies have logos online
- `"Failed to download from favicon"` - It tries multiple sources
- `"Using fallback service"` - Smart fallback system working

## 🆘 Need More Help?

1. **Check the main [README.md](../README.md)** for detailed options
2. **Look at [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for specific problems  
3. **Run with debug mode** to see what's happening:
   ```powershell
   python main.py --log-level DEBUG --input "your-file.xlsx" --output "logos"
   ```
4. **Check the log file** `temp/logo_scraper.log` for detailed information

## 🎉 Congratulations!

You're now ready to scrape company logos like a pro! 

**Next Steps:**
- Try different batch sizes for optimal performance
- Explore filtering options for large datasets  
- Check out the configuration file `src/config.py` for advanced settings
- Read the full documentation for power-user features

Happy logo scraping! 🎨
