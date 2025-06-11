# Troubleshooting

This guide addresses common issues and solutions for the Company Logo Scraper. For full CLI usage, run `python main.py --help` or see the README.

---

## Installation & Setup
- **Dependencies not installing?**
  - Run `python -m pip install --upgrade pip`
  - Use `./prepare_env.bat` to set up your environment
- **Wrong Python version?**
  - Use Python 3.7 or higher
- **Permission or path errors?**
  - Double-check your file paths and folder permissions

---

## Running the Tool
- **How do I specify input and output?**
  - Use `--input` (or `-i`) for your Excel file and `--output` (or `-o`) for the logo folder
  - Example: `python main.py --input "Companies.xlsx" --output "logos"`
- **How do I process only certain companies?**
  - Use `--id` (can be repeated) or `--filter "Column=Value"`
  - Example: `python main.py --id 12345 --id 67890`
  - Example: `python main.py --filter "Country=US"`
- **How do I speed up or slow down processing?**
  - Use `--batch-size` and `--max-processes` to control performance
  - Example: `python main.py --batch-size 100 --max-processes 4`

---

## Data & Results
- **No logos found?**
  - Check your input data for valid company names and website URLs
  - Ensure you have a working internet connection
  - Some companies may not have logos available from online sources
- **Output folder is empty or missing files?**
  - Make sure the output path exists and is writable
  - Check for typos in the `--output` argument
- **How does resume work?**
  - The tool automatically skips companies with existing logo files in the output folder
  - If you want to reprocess, delete the relevant PNGs from the output folder

---

## Advanced Usage
- **How do I debug issues?**
  - Add `--log-level DEBUG` to see detailed output in the console
- **How do I process a subset of companies?**
  - Use `--id` or `--filter` as above
- **How do I change defaults?**
  - Edit `src/config.py` for permanent changes (batch size, output folder, etc.)
  - CLI arguments always override config file values for a single run

---

## Common Problems & Fixes
- **Script crashes or exits early**
  - Check for error messages in the console
  - Make sure your input file is not open in another program
- **Logos are low quality or missing**
  - Some sources may only provide low-res images or none at all
  - Try increasing the batch size or running with different filters
- **Resume not working as expected**
  - The tool checks for `{ID}.png` files in the output folder to determine progress
  - If you change the input file, previously processed companies may be skipped or reprocessed

---

## Getting More Help
- Run `python main.py --help` for all CLI options
- See the README for usage examples and configuration tips
- Review [GETTING_STARTED.md](GETTING_STARTED.md) for setup
- If you still have issues, open an issue on GitHub with your command and error details
