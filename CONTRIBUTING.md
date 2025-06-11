# 🤝 Contributing to Company Logo Scraper

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/LogoScraper.git
   cd LogoScraper
   ```
3. **Set up development environment**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run tests** to ensure everything works:
   ```bash
   pytest tests/ -v
   ```

## 📋 Before You Start

- **Read the docs**: Check [docs/DECISIONS.md](docs/DECISIONS.md) for architectural principles
- **Understand the structure**: Review [docs/LEARNINGS.md](docs/LEARNINGS.md) for project insights
- **Check existing issues**: Look for open issues or discussions on GitHub

## 🛠️ Development Guidelines

### Code Style
- Follow existing code patterns and naming conventions
- Use meaningful variable names and clear comments
- Keep functions focused and modular
- Add docstrings for new classes and methods

### Testing
- Write tests for new features using pytest
- Ensure all tests pass: `pytest tests/ -v`
- Test both success and failure scenarios
- Add edge case tests where appropriate

### Documentation
- Update relevant documentation for new features
- Add examples to help users understand new functionality
- Update the CHANGELOG.md with your changes
- Consider adding troubleshooting notes if needed
- **If you change CLI arguments or configuration, update both `src/config.py` and all relevant documentation.**

## 🔧 Types of Contributions

### 🐛 Bug Reports
**Before reporting:**
- Check if the issue already exists
- Test with the latest version
- Include reproduction steps and error messages

**Good bug reports include:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Relevant log entries from `temp/logo_scraper.log`

### ✨ Feature Requests
**Before requesting:**
- Check if similar functionality exists
- Consider if it fits the project's scope
- Think about potential implementation approaches

**Good feature requests include:**
- Clear use case description
- Specific requirements
- Expected behavior
- Consideration of edge cases

### 🔧 Code Contributions

#### New Features
1. **Discuss first**: Open an issue to discuss the feature
2. **Start small**: Begin with a simple implementation
3. **Add tests**: Ensure comprehensive test coverage
4. **Update docs**: Add documentation and examples
5. **Follow patterns**: Use existing code as a guide

#### Bug Fixes
1. **Reproduce the bug**: Understand the issue completely
2. **Write a test**: Create a test that fails with the bug
3. **Fix the issue**: Make the minimal change needed
4. **Verify the fix**: Ensure the test passes and no regressions

#### Performance Improvements
1. **Measure first**: Benchmark current performance
2. **Profile the code**: Identify actual bottlenecks
3. **Test thoroughly**: Ensure functionality isn't broken
4. **Document gains**: Show before/after measurements

## 📁 Project Structure Understanding

```
src/
├── services/          # External integrations (APIs, data sources)
├── utils/            # Common utilities and helpers
├── config.py         # Centralized configuration
└── logo_scraper_core.py # Main orchestration logic

tests/                # Test suite
docs/                 # Documentation
temp/                 # Temporary files (gitignored)
```

### Key Modules
- **services/**: Each service handles a specific logo source (Clearbit, favicon, etc.)
- **utils/**: Reusable components (image processing, batch handling, etc.)
- **config.py**: All configuration in one place
- **main.py**: CLI entry point and orchestration

## 🧪 Testing Strategy

### Test Categories
- **Unit tests**: Individual function/class testing
- **Integration tests**: Component interaction testing
- **End-to-end tests**: Full pipeline testing
- **Configuration tests**: CLI and config validation

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_logo_scraper_core.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 📝 Pull Request Process

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes**: Follow the guidelines above
3. **Test thoroughly**: Run the full test suite
4. **Update documentation**: Add/update relevant docs
5. **Commit with clear messages**: Use descriptive commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Create pull request**: Use the GitHub interface

### Pull Request Checklist
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Documentation updated for any CLI/config changes
- [ ] CHANGELOG.md updated
- [ ] Code follows existing style
- [ ] No breaking changes (or clearly documented)

### Pull Request Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code review ready
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🎯 Areas Where Help is Needed

### High Priority
- Additional logo sources/APIs
- Performance optimizations
- Better error handling and recovery
- More comprehensive tests

### Medium Priority
- UI improvements for progress display
- Additional image processing options
- Better configuration validation
- Internationalization improvements

### Documentation
- More usage examples
- Video tutorials
- API documentation
- Performance tuning guides

## 🌟 Recognition

Contributors will be:
- Listed in the project's contributor list
- Mentioned in release notes for significant contributions
- Added to the AUTHORS file

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Ideas**: Start with a GitHub Discussion
- **Direct contact**: Check the README for maintainer contact info

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional tone

---

**Thank you for contributing to making Company Logo Scraper better! 🎨**
