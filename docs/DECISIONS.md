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
- **Input Service Tests**: Validation of data filtering and column normalization
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
- **Fallback**: Default Logo Generator with text-based company logos
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

## 5. Data Input and Filtering

### Implementation
- **Input Format**: Excel file with required fields (TPID, company name)
- **Filtering Options**: Command-line filters for flexible data selection
- **Normalization**: Automatic column name standardization
- **Validation**: Data integrity checks before processing

### Features
- Command-line filtering with `--filter` argument
- Specific TPID targeting with `--tpid` option
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
- Filtering by column values
- TPID-specific processing
- Temporary file management

---

# DECISIONS

## 2025-06-05: Professional Codebase Architecture and Release Infrastructure

### Code Organization Architecture
- **Src-Based Structure:** Adopted the `src/` layout pattern, moving all application code into a dedicated source directory. This decision improves import hygiene, prevents accidental execution of modules, and follows Python packaging best practices.
- **Consolidated Entry Point:** Created a single `main.py` file in the project root that serves as the sole entry point for the application. This consolidates CLI argument parsing and orchestration logic, eliminating the need for multiple CLI scripts and simplifying user interaction.
- **Module Separation:** Organized code into logical subdirectories (`services/` for external integrations, `utils/` for shared functionality) within the `src/` directory. This improves code discoverability and maintainability.
- **Test Organization:** Moved all tests to a root-level `tests/` directory, following Python community conventions and making tests easily discoverable for CI/CD systems.

### Import Strategy
- **Absolute Imports:** Standardized on absolute imports using the `src.` prefix throughout the codebase. This eliminates import ambiguity and makes the code more reliable across different execution contexts.
- **Bootstrap Solution:** Used `sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))` in the main entry point to enable src imports without requiring package installation. This provides a clean development experience while maintaining professional structure.

### Version and Release Management
- **Centralized Version Information:** Created `src/__version__.py` as the single source of truth for version information, author details, and project metadata. This enables consistent version display across CLI help text and configuration output.
- **Release Automation:** Developed comprehensive release infrastructure including:
  - `RELEASE_CHECKLIST.md`: Detailed checklist ensuring consistent release process
  - `release.ps1`: PowerShell automation script for release preparation
  - Automated cleanup procedures for development artifacts
- **Documentation Synchronization:** Established process for keeping README.md project structure in sync with actual codebase organization.

### Configuration Integration
- **CLI-Config Integration:** Validated that CLI arguments properly flow through the centralized CONFIG dictionary to all application layers (services, utilities, core logic). This ensures consistent behavior regardless of configuration source.
- **Path Management:** Implemented robust path handling for different execution contexts while maintaining clean separation between temporary files (`temp/`), source code (`src/`), and tests (`tests/`).

### Development Workflow
- **Incremental Restructuring:** Adopted an approach of making changes incrementally with testing at each step, reducing risk and enabling early detection of issues.
- **Clean Development Environment:** Established procedures for maintaining clean repository state through automated cleanup of `__pycache__` directories, temporary files, and test artifacts.
- **Professional Presentation:** Ensured all documentation, project structure, and release artifacts maintain professional standards suitable for open-source distribution.

### Rationale for Key Decisions

**Why src/ Layout?**
- Prevents accidental execution of modules when the project root is in PYTHONPATH
- Clearly separates source code from configuration, documentation, and test files  
- Standard pattern for Python packages intended for distribution
- Improves import hygiene and reduces namespace pollution

**Why Consolidated main.py?**
- Single, obvious entry point reduces user confusion
- Eliminates duplication of CLI parsing logic across multiple files
- Simplifies packaging and distribution
- Makes it easier to understand application flow

**Why Absolute Imports?**
- Eliminates import ambiguity and relative import complexity
- More reliable across different execution contexts
- Easier to understand and maintain
- Standard practice for production Python code

**Why Comprehensive Release Infrastructure?**
- Ensures consistent, reproducible releases
- Reduces human error in release process
- Provides clear documentation for contributors
- Enables automation and CI/CD integration
- Maintains professional project standards

## 2025-05-19: Robust Domain Cleaning and Diagnostics

- **Domain Cleaning:** The domain cleaning logic was significantly improved to handle malformed/invalid domains. It now removes unwanted characters (commas, semicolons, slashes, backslashes, quotes, angle brackets, parentheses, etc.), strips `www.`, handles multiple domains separated by delimiters, and removes leading/trailing dots and hyphens. Only the first valid domain is used.
- **Diagnostics & Logging:** Added detailed logging for Clearbit logo fetch failures, including HTTP status codes and response content. This enables better troubleshooting and transparency for why a logo fetch failed.
- **Pipeline Robustness:** The pipeline now gracefully handles malformed or invalid domains, only failing when a domain is truly unusable. This reduces false negatives and improves overall logo fetch rates.
- **Documentation:** Updated all relevant documentation and code docstrings to reflect these changes and ensure the workflow is clear and up-to-date.

## Previous Decisions
