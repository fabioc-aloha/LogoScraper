# Changelog

All notable changes to the Company Logo Scraper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-06-05

### Added
- **Visual Enhancement**: Added professional banner image to README.md
- **Documentation Organization**: 
  - Moved all documentation files to dedicated `docs/` folder
  - Created comprehensive documentation index in `docs/README.md`
  - Enhanced project structure documentation with data folder layout
- **User Experience Improvements**:
  - Added `example_companies.csv` for quick user onboarding
  - Created `CONTRIBUTING.md` with development guidelines
  - Enhanced `.gitignore` with comprehensive exclusion patterns
- **Testing Improvements**: Fixed all test suite issues and ensured 100% test pass rate

### Changed
- **Documentation Structure**: Reorganized all documentation into `docs/` folder for better navigation
- **README Enhancement**: Added banner image and improved data folder structure documentation
- **Project Organization**: Streamlined file organization for better maintainability

### Fixed
- **Test Suite**: Resolved all failing tests including file locking and import issues
- **Documentation Links**: Updated all internal documentation references to new `docs/` paths

## [Unreleased]

### Added
- Professional folder structure with `src/` directory
- Consolidated CLI entry point in root `main.py`
- Comprehensive documentation suite:
  - User-friendly `GETTING_STARTED.md` guide
  - Detailed `TROUBLESHOOTING.md` with common solutions
  - Technical `DECISIONS.md` and `LEARNINGS.md` for developers
- Version management system with author information
- Release automation script (`release.ps1`)
- Enhanced .gitignore with comprehensive project-specific exclusions
- Organized documentation in `docs/` folder

### Changed
- Restructured entire codebase to use `src/` layout
- Updated all imports to use absolute imports with `src.` prefix
- Moved CLI functionality from separate module into main entry point
- Reorganized test suite to dedicated `tests/` directory
- Streamlined README.md with better user experience
- Enhanced configuration system with proper CLI argument flow

### Fixed
- Configuration file syntax issues (escape sequences)
- Import path issues throughout codebase
- Test discovery and execution paths
- Temporary file organization and cleanup

## [1.0.0] - 2025-06-05

### Added
- Initial release of Company Logo Scraper
- Multi-source logo downloading (Clearbit API, favicons, text generation)
- Batch processing with parallel execution
- Progress tracking and resume capability
- Comprehensive logging and error handling
- Support for multiple languages and scripts
- Excel input/output with data enrichment
- Configurable filtering and processing options
- Rate limiting and retry mechanisms
- Image standardization to consistent PNG format

### Features
- **Multi-source Logo Acquisition**: Clearbit API, favicon extraction, text-based fallbacks
- **Batch Processing**: Efficient parallel processing of large datasets
- **Progress Tracking**: Resume interrupted processing sessions
- **Global Support**: Multilingual company name rendering with appropriate fonts
- **Data Enrichment**: Enhanced Excel output with processing results
- **Flexible Filtering**: Filter by country, TPID, or custom criteria
- **Quality Assurance**: Consistent 256×256 PNG output with proper transparency
- **Error Recovery**: Graceful handling of failures with detailed logging
- **Configuration**: Comprehensive settings via config file and CLI arguments

### Technical Highlights
- Modular architecture with services and utilities separation
- Comprehensive test suite with pytest
- Professional logging with configurable levels
- Session management and rate limiting
- Advanced domain extraction and cleaning
- Script-aware text rendering for non-Latin alphabets
- Image processing with quality preservation
- Resumable operations with progress persistence

---

## Release Notes Format

### [Version] - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed  
- Modifications to existing functionality

#### Deprecated
- Features that will be removed in future versions

#### Removed
- Features that have been removed

#### Fixed
- Bug fixes and corrections

#### Security
- Security-related improvements
