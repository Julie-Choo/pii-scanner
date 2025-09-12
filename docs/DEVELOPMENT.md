# docs/DEVELOPMENT.md
# Development Guide

## Setting Up Development Environment

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pii-scanner.git
cd pii-scanner

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_sm

# Install pre-commit hooks (optional)
pre-commit install
```

## Project Structure

The project follows a modular architecture:

```
pii-scanner/
├── src/pii_scanner/          # Core package
│   ├── core/                 # Core scanner functionality
│   │   ├── scanner.py        # Main scanner engine  
│   │   ├── models.py         # Data models
│   │   └── anonymizer.py     # Anonymization logic
│   ├── file_handlers/        # File type handlers
│   │   ├── base.py          # Base handler interface
│   │   ├── text_handler.py  # Text file handler
│   │   ├── csv_handler.py   # CSV handler
│   │   └── factory.py       # Handler factory
│   ├── utils/               # Utility modules
│   └── exceptions.py        # Custom exceptions
├── apps/                    # Applications
│   ├── streamlit/          # Web interface
│   └── api/                # REST API
├── tests/                  # Test suite
├── config/                 # Configuration files
└── docs/                   # Documentation
```

## Core Components

### Scanner Engine (`src/pii_scanner/core/scanner.py`)

The main `PIIScanner` class that orchestrates PII detection:

```python
class PIIScanner:
    def __init__(self):
        # Initialize Presidio engines
        
    def scan_text(self, text: str, options: ScanOptions) -> ScanResult:
        # Main scanning method
        
    def anonymize_text(self, text: str, options: ScanOptions) -> str:
        # Text anonymization
```

### Data Models (`src/pii_scanner/core/models.py`)

Core data structures:

- `PIIMatch`: Represents a detected PII entity
- `ScanResult`: Complete scan results with metadata
- `ScanOptions`: Configuration for scanning operations
- `FileInfo`: Information about files being scanned

### File Handlers (`src/pii_scanner/file_handlers/`)

Modular system for handling different file types:

```python
class BaseFileHandler(ABC):
    @abstractmethod
    def can_handle(self, file_info: FileInfo) -> bool:
        """Check if handler supports this file type"""
        
    @abstractmethod  
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        """Scan file for PII"""
```

## Adding New Features

### Adding a New File Handler

1. **Create the handler class:**

```python
# src/pii_scanner/file_handlers/excel_handler.py
from .base import BaseFileHandler
from ..core.models import FileInfo, ScanResult, ScanOptions

class ExcelFileHandler(BaseFileHandler):
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls']
    
    def can_handle(self, file_info: FileInfo) -> bool:
        return file_info.extension in self.SUPPORTED_EXTENSIONS
    
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        # Implementation here
        import pandas as pd
        
        # Read Excel file
        df = pd.read_excel(file_info.path)
        
        # Scan each cell (similar to CSV handler)
        matches = []
        # ... scanning logic ...
        
        return ScanResult(matches=matches)
```

2. **Register in factory:**

```python
# src/pii_scanner/file_handlers/factory.py
from .excel_handler import ExcelFileHandler

class FileHandlerFactory:
    def __init__(self, scanner):
        self.handlers = [
            # ... existing handlers ...
            ExcelFileHandler(scanner),
        ]
```

3. **Add tests:**

```python
# tests/test_file_handlers/test_excel_handler.py
class TestExcelFileHandler:
    def test_can_handle_excel(self, handler):
        file_info = FileInfo(extension=".xlsx")
        assert handler.can_handle(file_info)
        
    def test_scan_excel_file(self, handler):
        # Test implementation
```

### Adding a New PII Entity Type

1. **Update entity types:**

```python
# src/pii_scanner/core/models.py
class EntityType(Enum):
    # ... existing types ...
    EMPLOYEE_ID = "EMPLOYEE_ID"
```

2. **Add custom recognizer:**

```python
# src/pii_scanner/core/scanner.py
from presidio_analyzer import PatternRecognizer

def _add_custom_recognizers(self):
    employee_id_recognizer = PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        patterns=[{
            "name": "employee_id_pattern",
            "regex": r"\bEMP-\d{6}\b",
            "score": 0.8
        }],
        context=["employee", "emp id", "staff"]
    )
    
    self._analyzer.registry.add_recognizer(employee_id_recognizer)
```

3. **Add anonymization logic:**

```python
# src/pii_scanner/core/anonymizer.py
def _anonymize_employee_id(self, emp_id: str) -> str:
    """Anonymize employee ID"""
    return f"EMP-{emp_id[-3:]}" if len(emp_id) >= 3 else "EMP-***"
```

### Adding New API Endpoints

1. **Create route module:**

```python
# apps/api/routes/analytics.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_scan_statistics():
    """Get scanning statistics"""
    return {"total_scans": 1000, "entities_found": 5000}
```

2. **Include in main app:**

```python
# apps/api/main.py
from routes.analytics import router as analytics_router

app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
```

## Testing

### Running Tests

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test module  
pytest tests/test_core/test_scanner.py -v

# Run with coverage
pytest tests/ --cov=pii_scanner --cov-report=html

# Run tests in parallel
pytest tests/ -n auto
```

### Writing Tests

Follow the existing test patterns:

```python
class TestMyFeature:
    @pytest.fixture
    def my_fixture(self):
        return SomeTestData()
    
    def test_basic_functionality(self, scanner, my_fixture):
        """Test basic functionality"""
        result = scanner.some_method(my_fixture)
        
        assert result is not None
        assert len(result.matches) > 0
    
    def test_edge_cases(self, scanner):
        """Test edge cases"""
        # Test empty input
        result = scanner.some_method("")
        assert result.total_entities == 0
        
        # Test invalid input
        with pytest.raises(ValidationError):
            scanner.some_method(None)
```

### Test Structure

- `tests/conftest.py` - Shared fixtures
- `tests/test_core/` - Core functionality tests
- `tests/test_file_handlers/` - File handler tests  
- `tests/test_api/` - API endpoint tests
- `tests/fixtures/` - Test data files

## Code Quality

### Code Formatting

```bash
# Format code with Black
black src/ apps/ tests/

# Check code style with flake8
flake8 src/ apps/ tests/

# Sort imports
isort src/ apps/ tests/
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

### Type Hints

Use type hints throughout the codebase:

```python
from typing import List, Optional, Dict, Any

def process_results(
    matches: List[PIIMatch], 
    options: Optional[ScanOptions] = None
) -> Dict[str, Any]:
    """Process scan results"""
    return {"processed": True}
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def scan_text(self, text: str, options: Optional[ScanOptions] = None) -> ScanResult:
    """Scan text for PII entities.
    
    Args:
        text: The text to scan for PII
        options: Scanning configuration options
        
    Returns:
        ScanResult containing detected PII entities
        
    Raises:
        ScannerError: If scanning fails
        ValidationError: If input is invalid
        
    Example:
        >>> scanner = PIIScanner()
        >>> result = scanner.scan_text("Email: john@example.com")
        >>> print(result.total_entities)
        1
    """
```

### Updating Documentation

- Update `README.md` for new features
- Add examples to `docs/USAGE.md`
- Update API documentation in `docs/API.md`
- Add development notes to `docs/DEVELOPMENT.md`

## Debugging

### Logging

Use the built-in logging system:

```python
from pii_scanner.utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.debug("Starting processing")
    logger.info("Processing completed successfully")
    logger.warning("Potential issue detected")
    logger.error("Error occurred", exc_info=True)
```

### Common Issues

1. **Scanner not initializing:**
   - Check spaCy model is installed: `python -m spacy download en_core_web_sm`
   - Verify Presidio installation

2. **File encoding issues:**
   - Use the `chardet` library for encoding detection
   - Handle encoding errors gracefully

3. **Memory issues with large files:**
   - Process files in chunks
   - Use generators for large datasets

## Performance Considerations

### Optimization Tips

1. **Caching:** Cache scan results for repeated text
2. **Batch processing:** Process multiple texts together
3. **Async processing:** Use async/await for I/O operations
4. **Memory management:** Process large files in chunks

### Profiling

```python
import cProfile
import pstats

def profile_scanning():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your scanning code here
    result = scanner.scan_text(large_text)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime').print_stats(10)
```

## Release Process

1. **Update version:**
   - Update `__version__` in `src/pii_scanner/__init__.py`
   - Update version in `setup.py`

2. **Update changelog:**
   - Document new features and bug fixes
   - Follow semantic versioning

3. **Run full test suite:**
   ```bash
   python scripts/run_tests.py
   ```

4. **Build and test package:**
   ```bash
   python setup.py sdist bdist_wheel
   pip install dist/*.whl
   ```

5. **Create release:**
   - Tag the release: `git tag v1.0.0`
   - Push tags: `git push --tags`
   - Create GitHub release with changelog

## Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code style
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run the test suite** to ensure nothing is broken
6. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors introduced
```
