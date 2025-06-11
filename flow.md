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
└──────┬────────────┘
       ↓
┌──────┴────────────┐     ┌────────────────────┐
│ Enrichment & Log  │ →── │ download_progress, │
│                   │     │ logo_scraper.log   │
└───────────────────┘     └────────────────────┘
```

## Detailed Processing Flow
```
main.py
  ↓
Parse CLI args, set up logging, load config (config.py)
  ↓
Load input Excel file (input/Companies.xlsx or user-specified)
  ↓
For each batch of companies:
    process_batch()  # (utils/batch_processor.py)
      ↓
    For each company in batch:
        CompanyProcessor.process_company()  # (utils/company_processor.py)
          ↓
        1. Domain Extraction
            - Clean and normalize website/domain
            - Validate domain
          ↓
        2. Logo Acquisition
            - Try ClearbitService (services/clearbit_service.py)
            - Fallback to FaviconService (services/favicon_service.py)
            - Fallback to DefaultService (services/default_service.py)
          ↓
        3. Image Processing
            - Standardize logo (utils/image_resizer.py)
            - Validate size, format, and quality
          ↓
        4. Save Logo
            - Save as PNG to output folder (configurable)
          ↓
        5. Enrichment & Logging
            - Update progress (download_progress.json)
            - Log result (logo_scraper.log)
            - Save enriched Excel row if enabled
  ↓
After all batches:
    - Final summary log
    - Optionally clean temp files (cleanup.py)
```

## Logo Acquisition Service Flow
```
┌────────────────────────────┐
│ CompanyProcessor           │
└────────────┬───────────────┘
             ↓
   ┌─────────┴─────────┐
   │ Try Clearbit      │
   └─────────┬─────────┘
             ↓ (fail)
   ┌─────────┴─────────┐
   │ Try Favicon       │
   └─────────┬─────────┘
             ↓ (fail)
   ┌─────────┴─────────┐
   │ Generate Default  │
   └───────────────────┘
```

## Error Handling & Logging
```
┌────────────────────────────┐
│ Try/Except in Each Stage   │
└────────────┬───────────────┘
             ↓
   - Log error to logo_scraper.log
   - Mark company as failed in download_progress.json
   - Continue to next company (no crash)
```

## Key Supporting Modules
- main.py: Entry point, CLI, logging, config
- src/config.py: Central config, paths, batch size, etc.
- src/utils/batch_processor.py: Batch orchestration
- src/utils/company_processor.py: Per-company logic
- src/services/clearbit_service.py: Clearbit API
- src/services/favicon_service.py: Favicon fallback
- src/services/default_service.py: Default logo generator
- src/utils/image_resizer.py: Image standardization
- src/utils/progress_tracker.py: Progress tracking
- src/cleanup.py: Temp file cleanup
- download_progress.json: Progress state
- logo_scraper.log: Detailed logs
- input/Companies.xlsx: Input data
- output/: Logo PNGs
```
