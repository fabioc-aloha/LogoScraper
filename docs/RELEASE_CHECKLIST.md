# Release Checklist

This checklist ensures a consistent and reliable release process for the Company Logo Scraper project.

## Step 0: Manual Review & User Acceptance Testing (Human)
- [x] Manual review of all new/changed code
- [x] Manual performance and functional testing completed

## Step 1: Gather Release Information
- [x] Read `src/__version__.py` to determine:
    - Release version (e.g., __version__)
    - Release manager (e.g., __author__)
    - Release date (e.g., __build_date__)
    - Any other relevant metadata (email, description, etc.)

## Step 2: Pre-Release Preparation

### 2.1 Code Quality & Review
- [x] No linting errors or warnings (except line length and blank lines, which are ignored per .flake8 config)
- [x] Code follows project style guidelines
- [x] Code adheres to KISS (Keep It Simple, Stupid) principle
- [x] Code adheres to DRY (Don't Repeat Yourself) principle
- [x] Code follows PEP 8 (Python style guide, with exceptions for line length and blank lines)
- [x] All TODO/FIXME comments addressed or documented

### 2.2 Documentation Updates
- [x] `README.md` is up-to-date with latest features
- [x] `DECISIONS.md` updated with any architectural changes
- [x] `LEARNINGS.md` updated with any new insights
- [x] Command-line help text is accurate: `python main.py --help`
- [x] Configuration options in `config.py` are properly documented
- [x] Docstrings are complete and accurate
- [x] All CLI/configuration documentation matches the current codebase

### 2.3 Version Management
- [x] Update version number in `src/__version__.py`
- [x] Ensure version follows semantic versioning (MAJOR.MINOR.PATCH)
- [x] Update changelog/release notes
- [x] Version bump is appropriate for changes made

### 2.4 Requirements
- [x] No unused dependencies in `pyproject.toml`
- [x] All dependencies are necessary and secure
- [x] Modern Python environment uses `pyproject.toml` for dependency management (not requirements.txt)
- [x] `prepare_env.bat` and documentation reflect the modern config and install process

## Step 4: Git & GitHub Preparation

### 4.1 Repository Cleanup
- [ ] Remove temporary test files
- [ ] Clean up `__pycache__` directories
- [ ] Remove any sensitive data or credentials
- [ ] Ensure `.gitignore` is comprehensive
- [ ] Remove development artifacts

### 4.2 Commit Management
- [ ] All changes committed with descriptive messages
- [ ] Commit messages follow conventional commit format
- [ ] No merge conflicts
- [ ] Clean commit history (consider squashing if needed)

### 4.3 Branch Management
- [ ] Create release branch: `git checkout -b release/v<NEXT_VERSION>`
- [ ] Ensure main/master branch is up-to-date
- [ ] All feature branches merged or documented

## Step 5: Release Creation

### 5.1 GitHub Release
- [ ] Create new release on GitHub
- [ ] Use semantic version tag (e.g., `v<NEXT_VERSION>`)
- [ ] Write comprehensive release notes including:
  - [ ] New features
  - [ ] Bug fixes
  - [ ] Breaking changes (if any)
  - [ ] Performance improvements
  - [ ] Known issues

### 5.2 Release Assets
- [ ] Include source code (automatic)
- [ ] Include sample configuration files (if applicable)
- [ ] Include example input file template (if applicable)

## Step 6: Post-Release

### 6.1 Documentation Updates
- [ ] Update any external documentation
- [ ] Update project wiki (if exists)
- [ ] Notify relevant stakeholders

### 6.2 Monitoring
- [ ] Monitor for issues in the first 24-48 hours
- [ ] Check GitHub issues for bug reports
- [ ] Be prepared for hotfix if critical issues emerge

### 6.3 Next Version Planning
- [ ] Plan next version features
- [ ] Update project roadmap
- [ ] Document lessons learned from this release

## Step 7: Rollback Plan

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
| v1.0.0  | 2025-05-01 | Initial release with core functionality |
| v1.1.0  | 2025-06-05 | Documentation organization and visual enhancements |
| v<NEXT_VERSION> | <YYYY-MM-DD> | <Description for next release> |

---

## Checklist Summary

**Pre-Release** (Complete all before proceeding):
- [ ] Code quality review complete
- [ ] Documentation updated
- [ ] Version updated in all files

**Release Process**:
- [ ] Create release branch
- [ ] Final manual validation on release branch
- [ ] Create GitHub release with proper tags
- [ ] Write comprehensive release notes

**Post-Release**:
- [ ] Monitor for issues
- [ ] Plan next version
- [ ] Update documentation if needed

---

**Release Manager**: <Your Name>
**Release Date**: <YYYY-MM-DD>
**Release Version**: v<NEXT_VERSION>
**Notes**: <Summary of this release>
