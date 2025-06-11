# Codebase Flow: Company Logo Scraper

## High-Level Flow Diagram
```
┌──────────────┐
│   main.py    │
└──────┬───────┘
       ↓
┌──────┴────────────┐     ┌────────────────────┐
│  Config & Setup   │ ←── │  config.py, .env   │
└──────┬────────────┘     └────────────────────┘
       ↓
┌──────┴────────────┐     ┌──────────────────────┐
│  Input Data Load  │ ←── │ input/Companies.xlsx │
└──────┬────────────┘     └──────────────────────┘
       ↓
┌──────┴────────────┐     ┌────────────────────┐
│ Filter Existing   │ ←── │ Check output/*.png │
│    Logos          │     │ Skip processed IDs │
└──────┬────────────┘     └────────────────────┘
       ↓
┌──────┴────────────┐
│ Batch Processing  │
└──────┬────────────┘
       ↓
┌──────┴────────────┐
│ CompanyProcessor  │
└──────┬────────────┘
       ↓
┌──────┴────────────┐     ┌────────────────────┐
│ Logo Acquisition  │ ←── │ Clearbit, Favicon, │
│  (Service Layer)  │     │ Default Generator  │
└──────┬────────────┘     └────────────────────┘
       ↓
┌──────┴────────────┐
│ Image Resizing    │
└──────┬────────────┘
       ↓
┌──────┴────────────┐
│ Save Logo File    │
└───────────────────┘
```

## Detailed Processing Flow
```
main.py
  ↓
Parse CLI args, load config (config.py)
  ├── New standardized CLI: --id (replaces deprecated --tpid)
  └── Support for multiple ID filtering: --id 123 --id 456
  ↓
Load input Excel file (input/Companies.xlsx or user-specified)
  ├── Expected columns: ID, CompanyName, WebsiteURL, Country
  └── Filter by country, ID, or custom criteria
  ↓
Filter existing logos from output folder
  ├── Check for existing {ID}.png files in output directory
  ├── Skip companies that already have logos (resumable operation)
  ├── Report count of existing vs. remaining companies
  └── Exit early if all companies already processed
  ↓
Processing {total} companies in {batches} batches...
  ↓
For each batch of companies:
    process_batch()  # (utils/batch_processor.py)
      ├── Batch size of 300 for optimal memory/parallelism
      ├── Worker pool sized to (CPU cores - 1)
      ├── Clean progress messages (no overlapping progress bars)
      ├── Periodic status updates every 25 companies
      └── ETA estimation based on average batch processing time
      ↓
    For each company in batch:
        CompanyProcessor.process_company()  # (utils/company_processor.py)
          ↓
        1. Domain Extraction & Validation
            - Clean and normalize WebsiteURL/domain
              ├── Remove unwanted characters and delimiters
              ├── Strip www and common prefixes
              ├── Handle multiple domains in field
              └── Remove leading/trailing dots and hyphens
            - Enhanced domain validation
              ├── Minimum length (4 chars) and must contain dot
              ├── Valid TLD (at least 2 characters)
              ├── No empty domain parts
              └── Prevents invalid domains like single characters
          ↓
        2. Logo Acquisition
            - Try ClearbitService (with improved error handling)
            - On fail, try FaviconService (DuckDuckGo/Google S2)
            - Last resort: DefaultService with text rendering
              ├── Uses CompanyName initials (up to 4 chars)
              └── Square background without rounded corners
          ↓
        3. Enhanced Image Processing
            - Standardize logo (utils/image_resizer.py)
              ├── Target size: 256x256 pixels 
              ├── Minimum size: 24x24 pixels
              ├── PNG format with transparency
              └── Improved palette image handling (eliminates PIL warnings)
            - Validate image integrity
          ↓
        4. Save Logo
            - Save as {ID}.png to output folder
            - Overwrites existing files (no skip-existing check)
  ↓
After all batches:
    - Generate final summary statistics
    - Clean progress display with success rates
```

## Logo Acquisition Service Flow
```
┌────────────────────────────┐
│ CompanyProcessor           │
└────────────┬───────────────┘
             ↓
   ┌─────────┴─────────┐
   │ Try Clearbit      │
   └─────────┬─────────┘     HTTP retry logic
             ↓ (fail)
   ┌─────────┴─────────┐
   │ Try Favicon       │ ←── DuckDuckGo, then
   └─────────┬─────────┘     Google S2 fallback
             ↓ (fail)
   ┌─────────┴─────────┐
   │ Generate Default  │ ←── Company initials
   └───────────────────┘     Square background
```

## Key Supporting Modules
- main.py: Entry point, CLI with --id argument, config
- src/config.py: Central config, paths, batch size, etc.
- src/logo_scraper_core.py: Main orchestration and company processing pipeline
- src/utils/batch_processor.py: Parallel batch processing with clean progress display
- src/utils/company_processor.py: Per-company orchestration and logo acquisition
- src/services/clearbit_service.py: Clearbit API integration with enhanced error handling
- src/services/favicon_service.py: Favicon discovery and fetch
- src/services/default_service.py: Default logo generation using company initials
- src/services/input_data_service.py: Data loading and standardized column handling
- src/utils/url_utils.py: Enhanced URL/domain normalization and validation
- src/utils/image_resizer.py: Image standardization with improved palette handling
- src/utils/progress_tracker.py: Progress persistence for resumable operations

## Recent Improvements (v1.5.x)

### CLI & Data Standardization
- **Migrated CLI**: `--tpid` → `--id` for better standardization
- **Column Names**: Proprietary names → Public standard names
  - `tpid` → `ID`
  - `crmaccountname` → `CompanyName` 
  - `websiteurl` → `WebsiteURL`
  - `country` → `Country`
- **Multiple ID Support**: `--id 123 --id 456` for targeted processing

### Enhanced Progress Display
- **Removed overlapping progress bars** that caused display truncation
- **Clean batch progress messages** with intuitive status emojis:
  - 🟩 Excellent success (≥90% logos found)
  - 🟨 Good success (50-89% logos found) 
  - 🟥 Poor success (0-49% logos found)
- **Periodic updates** every 25 companies to avoid output flooding
- **Clear completion summaries** for each batch with success rates
- **ETA estimation** shows remaining time based on average batch processing speed

### Improved Error Handling
- **Enhanced domain validation** prevents invalid single-character domains
- **Better image processing** eliminates PIL palette transparency warnings
- **Robust API error handling** with detailed logging for troubleshooting

### File Handling
- **Overwrites existing logos** by default (no skip-existing check)
- **Progress tracking separate** from file existence
- **Standardized column handling** throughout pipeline
- **Smart resume capability** automatically skips companies with existing logos
- **Incremental processing** allows adding new companies without reprocessing existing ones
