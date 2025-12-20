# Contributing to ToniSynthFunc

Thank you for your interest in contributing to ToniSynthFunc! This guide will help you get started.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Using GitHub Copilot](#using-github-copilot)

## Code of Conduct

Please be respectful and constructive in all interactions. We're building something together!

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Azure Functions Core Tools
- Azure subscription (for testing against Azure services)
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kingersoll_microsoft/ToniText2Speech.git
   cd ToniText2Speech
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure local settings**
   Copy `local.settings.json.example` to `local.settings.json` and fill in your Azure credentials:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "SPEECH_SERVICE_KEY": "your-speech-key",
       "SPEECH_SERVICE_REGION": "westus2",
       "STORAGE_ACCOUNT_NAME": "your-storage-account",
       "STORAGE_ACCOUNT_KEY": "your-storage-key",
       "STORAGE_CONTAINER_NAME": "audio-files"
     }
   }
   ```

5. **Run tests**
   ```bash
   pytest -v
   ```

6. **Start local server**
   ```bash
   func start
   ```

## Making Changes

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Messages
Follow conventional commits format:
```
type(scope): description

feat(voices): add support for whispering style
fix(validation): handle empty text input
docs(api): update endpoint documentation
test(markdown): add table removal tests
```

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following coding standards
3. **Add/update tests** for your changes
4. **Update documentation** if needed
5. **Run the test suite** to ensure nothing is broken
6. **Submit a PR** with a clear description

### PR Checklist
- [ ] Tests added/updated and passing
- [ ] Type hints included
- [ ] Docstrings added for new functions
- [ ] API documentation updated (if applicable)
- [ ] No linting errors

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions
- Use f-strings for string formatting

### Example Function
```python
def process_text(text: str, options: dict | None = None) -> str:
    """
    Process text for speech synthesis.
    
    Args:
        text: The input text to process
        options: Optional processing options
        
    Returns:
        Processed text ready for synthesis
        
    Raises:
        ValidationError: If text is empty or invalid
    """
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty", field="text")
    
    # Process the text...
    return processed_text
```

### Error Handling
- Use custom exceptions from `exceptions.py`
- Use HTTP helpers from `http_helpers.py` for API responses
- Always log errors with context

### File Organization
```
tonisynthfunc/
├── function_app.py      # HTTP endpoints only
├── character_voices.py  # Voice/dialogue logic
├── validators.py        # Input validation
├── exceptions.py        # Custom exceptions
├── http_helpers.py      # Response utilities
└── tests/
    └── test_*.py        # One test file per module
```

## Testing Requirements

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific file
pytest tests/test_validators.py

# Verbose output
pytest -v
```

### Test Structure
```python
class TestFeatureName:
    """Tests for feature_name functionality."""
    
    def test_success_case(self):
        """Test normal/expected behavior."""
        result = function_under_test(valid_input)
        assert result == expected_output
    
    def test_edge_case(self):
        """Test boundary conditions."""
        result = function_under_test(edge_input)
        assert result == expected_output
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValidationError):
            function_under_test(invalid_input)
```

### Coverage Requirements
- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Using GitHub Copilot

This repository is optimized for GitHub Copilot agent mode. See `.github/copilot-instructions.md` for:
- Project structure overview
- Code patterns and conventions
- Common implementation tasks
- Testing guidelines

### Creating Agent-Friendly Issues
When creating issues for Copilot to work on:
1. Use the "Copilot Agent Task" template
2. List specific files to modify
3. Include clear acceptance criteria
4. Provide code context and examples
5. Define what's out of scope

### Labels for Copilot
- `copilot-agent` - Tasks suitable for Copilot coding agent
- `copilot-ready` - Well-specified issues ready for agent work
- `good-first-issue` - Simple tasks for getting started

## Questions?

- Check `API_DOCUMENTATION.md` for API details
- Review existing code for patterns
- Open an issue for discussion

Thank you for contributing! 🎉
