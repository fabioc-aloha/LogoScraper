# Release Checklist

This checklist ensures a consistent and reliable release process for the Company Logo Scraper project.

## Pre-Release Preparation

### 1. Code Quality & Testing ✅
- [x] All tests pass: `pytest src/tests/ -v`
- [x] Configuration flow tests pass: `python test_config_flow.py`
- [x] CLI configuration tests pass: `python test_cli_config.py`
- [x] End-to-end configuration tests pass: `python test_end_to_end_config.py`
- [x] No linting errors or warnings
- [x] Code follows project style guidelines
- [x] All TODO/FIXME comments addressed or documented

### 2. Documentation Updates ✅
- [x] `README.md` is up-to-date with latest features
- [x] `DECISIONS.md` updated with any architectural changes
- [x] `LEARNINGS.md` updated with any new insights
- [x] Command-line help text is accurate: `python main.py --help`
- [x] Configuration options in `config.py` are properly documented
- [x] Docstrings are complete and accurate

### 3. Version Management ✅
- [x] Update version number in relevant files (see Version Update section below)
- [x] Ensure version follows semantic versioning (MAJOR.MINOR.PATCH)
- [x] Update changelog/release notes
- [x] Version bump is appropriate for changes made

## Version Update Steps

### 1. Update Version Information
Create/update a `__version__.py` file in the `src/` directory:
```python
# src/__version__.py
__version__ = "1.2.0"
__author__ = "Your Name"
__email__ = "your.email@domain.com"
__description__ = "Company Logo Scraper - Robust logo collection utility"
```

### 2. Update Main Module
Add version import to `main.py`:
```python
# Add after existing imports
try:
    from src.__version__ import __version__
except ImportError:
    __version__ = "unknown"

# Update argument parser description
parser = argparse.ArgumentParser(
    description=f'Company Logo Scraper v{__version__}',
    # ... rest of parser config
)
```

### 3. Update Configuration
Add version to `src/config.py`:
```python
# Add at the top after imports
try:
    from .__version__ import __version__
except ImportError:
    __version__ = "unknown"

# Add to CONFIG dictionary
CONFIG = {
    'VERSION': __version__,
    # ... existing config options
}
```

### 4. Update Requirements (if needed)
- [ ] `requirements.txt` has correct dependency versions
- [ ] No unused dependencies
- [ ] All dependencies are necessary and secure

## Testing & Validation

### 1. Functional Testing ✅
- [ ] Test with small dataset (5-10 companies)
- [ ] Test CLI argument parsing: `python main.py --help`
- [ ] Test configuration updates work correctly
- [ ] Test filtering functionality: `--filter "country=US"`
- [ ] Test TPID filtering: `--tpid 12345`
- [ ] Test batch processing with different batch sizes
- [ ] Test parallel processing with different process counts
- [ ] Test temp folder cleanup: `--clean`

### 2. Error Handling ✅
- [ ] Test with invalid input file path
- [ ] Test with malformed Excel file
- [ ] Test with missing required columns
- [ ] Test network timeout scenarios
- [ ] Test disk space limitations
- [ ] Test permission errors

### 3. Performance Testing ✅
- [ ] Test with larger dataset (100+ companies)
- [ ] Monitor memory usage during processing
- [ ] Verify reasonable processing speeds
- [ ] Check for memory leaks in long-running processes

## Git & GitHub Preparation

### 1. Repository Cleanup ✅
- [ ] Remove temporary test files
- [ ] Clean up `__pycache__` directories: `Remove-Item -Recurse -Force __pycache__`
- [ ] Remove any sensitive data or credentials
- [ ] Ensure `.gitignore` is comprehensive
- [ ] Remove development artifacts

### 2. Commit Management ✅
- [ ] All changes committed with descriptive messages
- [ ] Commit messages follow conventional commit format
- [ ] No merge conflicts
- [ ] Clean commit history (consider squashing if needed)

### 3. Branch Management ✅
- [ ] Create release branch: `git checkout -b release/v1.2.0`
- [ ] Ensure main/master branch is up-to-date
- [ ] All feature branches merged or documented

## Release Creation

### 1. GitHub Release ✅
- [ ] Create new release on GitHub
- [ ] Use semantic version tag (e.g., `v1.2.0`)
- [ ] Write comprehensive release notes including:
  - [ ] New features
  - [ ] Bug fixes
  - [ ] Breaking changes (if any)
  - [ ] Performance improvements
  - [ ] Known issues

### 2. Release Notes Template
```markdown
## Company Logo Scraper v1.2.0

### 🚀 New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Fix 1 description
- Fix 2 description

### 🔧 Improvements
- Improvement 1 description
- Improvement 2 description

### 📚 Documentation
- Documentation update 1
- Documentation update 2

### 🧪 Testing
- Test improvement 1
- Test improvement 2

### 📦 Dependencies
- Dependency updates (if any)

### ⚠️ Breaking Changes
- Breaking change 1 (if any)
- Migration instructions

### 🔗 Installation
\```bash
pip install -r requirements.txt
\```

### 🏃‍♂️ Quick Start
\```bash
python main.py --input "path/to/companies.xlsx" --output "path/to/logos"
\```
```

### 3. Release Assets ✅
- [ ] Include source code (automatic)
- [ ] Include sample configuration files (if applicable)
- [ ] Include example input file template (if applicable)

## Post-Release

### 1. Documentation Updates ✅
- [ ] Update any external documentation
- [ ] Update project wiki (if exists)
- [ ] Notify relevant stakeholders

### 2. Monitoring ✅
- [ ] Monitor for issues in the first 24-48 hours
- [ ] Check GitHub issues for bug reports
- [ ] Be prepared for hotfix if critical issues emerge

### 3. Next Version Planning ✅
- [ ] Plan next version features
- [ ] Update project roadmap
- [ ] Document lessons learned from this release

## Rollback Plan

### If Issues Are Discovered ⚠️
1. **Minor Issues**: Document in known issues, plan hotfix
2. **Major Issues**: Consider reverting release, publish hotfix
3. **Critical Issues**: Immediately revert, publish emergency fix

### Rollback Steps
- [ ] Revert to previous stable tag
- [ ] Communicate issue to users
- [ ] Publish fix as patch version
- [ ] Update release notes with fix information

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0.0  | YYYY-MM-DD | Initial release |
| v1.1.0  | YYYY-MM-DD | Added feature X |
| v1.2.0  | YYYY-MM-DD | Current release |

---

## Checklist Summary

**Pre-Release** (Complete all before proceeding):
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version updated in all files

**Release Process**:
- [ ] Create release branch
- [ ] Final testing on release branch
- [ ] Create GitHub release with proper tags
- [ ] Write comprehensive release notes

**Post-Release**:
- [ ] Monitor for issues
- [ ] Plan next version
- [ ] Update documentation if needed

---

**Release Manager**: ________________  
**Release Date**: ________________  
**Release Version**: ________________  
**Notes**: ________________
