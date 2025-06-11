# Release Checklist

## Pre-Release
- [ ] Review and test all code changes
- [ ] Ensure all tests pass (`pytest tests/`)
- [ ] Update documentation (README, GETTING_STARTED, TROUBLESHOOTING, etc.)
- [ ] Bump version in `src/__version__.py`
- [ ] Update `CHANGELOG.md` with new version and changes
- [ ] Check for unused files, dead code, and outdated references
- [ ] Verify CLI help text is accurate (`python main.py --help`)
- [ ] Ensure all configuration and CLI options are documented

## Release
- [ ] Commit all changes with a clear message
- [ ] Tag the release in git (e.g., `vX.Y.Z`)
- [ ] Push branch and tag to GitHub
- [ ] Create a new GitHub release with:
  - [ ] Release notes (summary of changes, new features, fixes)
  - [ ] Link to `CHANGELOG.md`
  - [ ] Attach sample data or config if needed

## Post-Release
- [ ] Monitor for issues and bug reports
- [ ] Respond to user feedback and questions
- [ ] Plan next version/features
- [ ] Update project roadmap if needed

See README for usage, CONTRIBUTING.md for PRs.
