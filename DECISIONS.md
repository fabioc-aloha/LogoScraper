# Purpose and Goals

## Overview
The Company Logo Scraper efficiently acquires and standardizes company logos at scale, providing an automated solution for organizations needing consistent visual assets for business applications, CRM systems, or corporate directories.

## Core Goals
1. **Automated Logo Acquisition**:
   - Reliable fetching from authoritative sources with fallback mechanisms
   - Support for high-volume parallel processing
   - Handling of diverse company naming patterns and languages

2. **Quality Assurance**:
   - Consistent logo dimensions, format and visual quality
   - Proper transparency and background handling
   - Image integrity validation

3. **Performance and Reliability**:
   - Efficient parallel processing with robust error handling
   - Progress tracking and resume capabilities
   - Caching to minimize redundant operations

4. **Data Management**:
   - Comprehensive processing status tracking
   - Enriched output with processing metadata
   - Support for incremental processing of large datasets

## Success Criteria
- Logo acquisition success rate >90% from primary sources
- Consistent 512×512 PNG output format with standardized quality
- Efficient resource management for parallel processing
- Comprehensive error handling and logging
- Processing thousands of companies with minimal manual intervention

---

# Architectural Decisions

## 1. Code Organization

### Implementation
- **Module Structure**: Services for external integrations, utilities for common functions
- **Centralized Configuration**: Single config.py for all settings
- **Documentation**: Comprehensive code documentation and README
- **Modular Plugin System**: Extensible architecture for logo sources

### Pending Improvements
- Additional plugin discovery mechanism
- Service health monitoring and performance dashboards

### Test Suite
- **Input Service Tests**: Validation of input data and column normalization
- **Logo Generation Tests**: End-to-end validation of the generation pipeline
- **Multilingual Text Tests**: Special test cases for challenging scripts and languages

## 2. Storage Structure

### Implementation
```
C:\Data\
    ├── logos\     # Processed company logos
    ├── temp\      # Temporary files
    └── input\     # Input Excel files
```

- **Automated Management**: Temp file cleanup with user confirmation
- **Consistent Access**: Standard paths through configuration
- **Clear Organization**: Separate directories for different data types

## 3. Logo Processing Pipeline

### Implementation
- **Primary Source**: Clearbit Logo API
- **Fallback**: DuckDuckGo and Google S2 favicon services (no direct site scraping)
- **Image Requirements**: 512×512 PNG format with consistent quality
- **Multilingual Support**: Comprehensive language and script detection

### Features
- Intelligent script detection for company names
- Support for all major writing systems (Latin, CJK, Cyrillic, etc.)
- Optimized font selection based on detected script
- Improved text positioning and layout
- Comprehensive international character rendering

### Algorithm Details
- **Script Detection**: Multi-phase analysis of Unicode character properties with special handling for Turkish, Korean, and mixed-script text
- **Text Rendering**: Three-tiered fallback system with specialized handling for complex scripts
- **Image Processing**: Aspect ratio preservation with centered positioning and anti-aliased LANCZOS resampling

### Recent Updates
- Default logos now use square backgrounds (no rounded corners) and support up to 4-character initials for better handling of long company names

## 4. Service Layer Design

### Implementation
- **Service Boundaries**: One service per external API integration
- **Consistent Interfaces**: Standard methods and error handling
- **Performance**: HTTP retry logic with exponential backoff
- **Reliability**: Rate limiting and request throttling

### Features
- Service-level metrics collection
- Local response caching 
- Centralized error handling and logging
- Shared HTTP client configuration

## 5. Data Input and Selection

### Implementation
- **Input Format**: Excel file with required fields (TPID, company name)
- **Selection Options**: Command-line options for limiting input (e.g., --top, --tpid)
- **Normalization**: Automatic column name standardization
- **Validation**: Data integrity checks before processing

### Features
- Specific TPID targeting with `--tpid` option
- Limit processing to the first N companies with `--top` option
- Detailed error reporting for invalid data

### Pending Improvements
- Fuzzy matching for company names
- Domain name inference from company names

## 6. Error Management

### Implementation
- **Comprehensive Logging**: Detailed error and progress tracking
- **Recovery Mechanisms**: Automatic retries with exponential backoff
- **Progress Preservation**: Resume capability after interruptions
- **Transparency**: Clear error messages and status reporting

### Features
- Detailed company processing information
- Success/failure tracking by source
- Batch progress statistics with completion percentage
- Time-based estimates (elapsed and remaining)
- Structured error categorization and reporting

### Pending Improvements
- Error trend analysis and impact assessment
- Alert thresholds for critical errors

## 7. Parallel Processing

### Implementation
- **Batch Processing**: Configurable batch size (default: 300)
- **Resource Management**: Controlled parallel execution
- **Progress Tracking**: Detailed status reporting during execution
- **Command-line Control**: Adjustable workers and batch size

### Features
- Per-company progress tracking
- Overall progress percentage calculation
- Time-based progress estimates
- Resource cleanup and optimization

## 8. HTTP Handling

### Implementation
- **Session Management**: Consistent configuration across services
- **Rate Limiting**: Service-specific request throttling
- **Error Handling**: Automatic retries for transient failures
- **Reliability**: Connection pooling and request optimization

### Features
- Robust retry logic with exponential backoff
- Intelligent handling of different error types
- Configurable retry attempts and delay
- Detailed error logging during retries

## 9. Configuration Management

### Implementation
- **Centralized Settings**: Single config.py with logical groupings
- **Command-line Options**: Flexible runtime configuration
- **Validation**: Startup configuration verification
- **Defaults**: Sensible preset values for all settings
- **Documentation**: Comprehensive parameter descriptions with recommendations

### Features
- Command-line argument support for all key settings
- Robust argument parsing with detailed help text
- Configuration parameter validation at startup
- Progressive configuration override system
- Performance optimization guidance for key parameters

## 10. Command-Line Interface

### Implementation
- **User-Friendly Options**: Simple flags for common operations
- **Configuration Override**: Runtime adjustment without editing files
- **Multiple Values**: Support for repeated options (e.g., multiple TPIDs)
- **Help System**: Detailed usage information for all commands

### Features
- Custom input/output paths
- Batch size and parallelism control
- Logging level configuration
- TPID-specific processing
- Temporary file management

---

# DECISIONS

## 2025-05-19: Robust Domain Cleaning and Diagnostics

- **Domain Cleaning:** The domain cleaning logic was significantly improved to handle malformed/invalid domains. It now removes unwanted characters (commas, semicolons, slashes, backslashes, quotes, angle brackets, parentheses, etc.), strips `www.`, handles multiple domains separated by delimiters, and removes leading/trailing dots and hyphens. Only the first valid domain is used.
- **Minimum Logo Size:** The minimum acceptable logo size is now **28x28 pixels** (was 32x32). Images below this threshold are considered too low quality and are skipped.
- **Diagnostics & Logging:** Added detailed logging for Clearbit logo fetch failures, including HTTP status codes and response content. This enables better troubleshooting and transparency for why a logo fetch failed.
- **Pipeline Robustness:** The pipeline now gracefully handles malformed or invalid domains, only failing when a domain is truly unusable. This reduces false negatives and improves overall logo fetch rates.
- **Documentation:** Updated all relevant documentation and code docstrings to reflect these changes and ensure the workflow is clear and up-to-date.

## May 2025: Minimum Logo Size and Upscaling
- Decision: Only one dimension (width or height) must be >= MIN_SOURCE_SIZE for a logo to be accepted.
- Decision: Remove the upscaling ratio limit; upscaling is now only limited by the configured output size.
- Rationale: This enables more favicons and small logos to be visually inspected and gives users more flexibility.

## Previous Decisions
