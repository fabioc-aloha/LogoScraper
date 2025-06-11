# 🔧 Troubleshooting Guide

Common issues and solutions for the Company Logo Scraper.

## 🚨 Installation Issues

### Dependencies Won't Install
**Problem:** `pip install -r requirements.txt` fails

**Solutions:**
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Install with verbose output to see what's failing
pip install -r requirements.txt -v

# If specific packages fail, install them individually
pip install pandas openpyxl requests pillow
```

### Python Version Issues
**Problem:** Script won't run or imports fail

**Solution:** Ensure you're using Python 3.7 or higher:
```bash
python --version
# Should show Python 3.7.0 or higher
```

## 📁 File Path Issues

### Excel File Not Found
**Problem:** `FileNotFoundError: [Errno 2] No such file or directory`

**Solutions:**
- Use absolute paths: `python main.py --input "C:\\Full\\Path\\To\\File.xlsx"`
- Check file exists: Verify the file path is correct
- Use forward slashes or escaped backslashes on Windows

### Permission Denied
**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**
- Close Excel if the input file is open
- Run as administrator if needed
- Check folder write permissions for output directory

## 🌐 Network/API Issues

### Clearbit API Failures
**Problem:** High failure rate or API errors

**Solutions:**
- Check your internet connection
- Verify Clearbit API key if using paid tier
- Reduce batch size: `--batch-size 50`
- Reduce parallel processes: `--max-processes 2`

### Favicon Download Failures
**Problem:** Many companies showing "No logo found"

**Solutions:**
- Check `logo_scraper.log` for specific error details
- Some domains may block automated requests
- Consider using VPN if regional blocking is suspected

## 💾 Memory Issues

### Out of Memory Errors
**Problem:** Script crashes with memory errors

**Solutions:**
```bash
# Reduce batch size
python main.py --batch-size 100

# Reduce parallel processes  
python main.py --max-processes 4

# Process in smaller chunks using filters
python main.py --filter "country=US"
```

## 🔄 Processing Issues

### Script Hangs or Freezes
**Problem:** Processing stops without completion

**Solutions:**
```bash
# Enable debug logging to see what's happening
python main.py --log-level DEBUG

# Reduce parallelism to isolate issues
python main.py --max-processes 1

# Clear temporary files and restart
python main.py --clean
```

### Resume Not Working
**Problem:** Script doesn't resume from where it left off

**Solutions:**
- Check if `temp/download_progress.json` exists
- Don't use `--clean` if you want to resume
- Verify input file hasn't changed since last run

## 📊 Data Issues

### Wrong Column Names
**Problem:** `KeyError` or "Column not found" errors

**Solution:** Ensure your Excel file has these columns:
- `ID` (required) - Unique company identifier
- `CompanyName` (required) - Company name
- `WebsiteURL` (optional) - Website URL
- `Country` (optional) - Country code for filtering

### Empty Results
**Problem:** No logos downloaded despite valid input

**Solutions:**
- Check company names are valid and not empty
- Verify website URLs are properly formatted
- Enable debug logging: `--log-level DEBUG`
- Check `logo_scraper.log` for detailed error information

## 🖼️ Image Quality Issues

### Blurry or Low-Quality Logos
**Problem:** Generated logos look poor

**Solutions:**
- Increase output size in `src/config.py`: `OUTPUT_SIZE = 512`
- Check source image quality - low resolution sources will remain low quality
- Text-based logos depend on font availability

### Text Rendering Issues
**Problem:** Non-English company names display as boxes or incorrectly

**Solutions:**
- Install additional fonts for your language
- Check Windows/Mac font settings
- Report specific language issues for potential fixes

## 🧹 Cleanup Issues

### Temporary Files Won't Delete
**Problem:** `--clean` option fails or temp files persist

**Solutions:**
```bash
# Manual cleanup
rm -rf temp/
# or on Windows:
rmdir /s temp

# Then restart
python main.py
```

## 📝 Logging and Debugging

### Enable Detailed Logging
```bash
# See everything that's happening
python main.py --log-level DEBUG

# Check the log file for detailed error information
cat temp/logo_scraper.log
# or on Windows:
type temp\logo_scraper.log
```

### Common Log Messages
- `"Domain cleaning result"` - Shows how website URLs are processed
- `"No logo found for company"` - Company had no downloadable logo
- `"API rate limit exceeded"` - Slow down processing with smaller batch sizes
- `"Failed to download"` - Network or server issues with specific URLs

## 🆘 Still Need Help?

1. **Check the log file** `temp/logo_scraper.log` for detailed error messages
2. **Run with debug logging** `--log-level DEBUG` to see what's happening
3. **Try a smaller test** with just a few companies first
4. **Check the GitHub issues** for similar problems and solutions
5. **Create a new issue** with:
   - Your command line
   - Error message
   - Sample of your input data (with sensitive info removed)
   - Your operating system and Python version

## 📋 Quick Diagnostic Checklist

Before reporting an issue, try:

- [ ] Python 3.7+ installed and working
- [ ] All dependencies installed successfully  
- [ ] Input Excel file has required columns (`ID`, `CompanyName`, `WebsiteURL`, `Country`)
- [ ] Input file path is correct and accessible
- [ ] Output directory exists and is writable
- [ ] Internet connection is working
- [ ] No antivirus blocking the script
- [ ] Tried with `--log-level DEBUG` to see detailed output
- [ ] Checked `temp/logo_scraper.log` for error details
