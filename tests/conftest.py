# tests/conftest.py
"""
Test configuration and fixtures
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pii_scanner import PIIScanner, ScanOptions
from pii_scanner.file_handlers import FileHandlerFactory

@pytest.fixture(scope="session")
def scanner():
    """Create scanner instance for tests"""
    return PIIScanner()

@pytest.fixture(scope="session") 
def file_factory(scanner):
    """Create file handler factory for tests"""
    return FileHandlerFactory(scanner)

@pytest.fixture
def sample_pii_text():
    """Sample text containing various PII types"""
    return """
    Contact Information:
    Name: John Doe
    Email: john.doe@company.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    Address: 123 Main Street, New York, NY 10001
    Credit Card: 4532-1234-5678-9012
    """

@pytest.fixture
def scan_options():
    """Default scan options for testing"""
    return ScanOptions(
        confidence_threshold=0.5,
        include_context=True,
        context_window=50
    )

@pytest.fixture
def temp_text_file():
    """Create temporary text file with PII"""
    content = "Contact john.doe@email.com or call (555) 123-4567"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass

@pytest.fixture
def temp_csv_file():
    """Create temporary CSV file with PII"""
    content = """Name,Email,Phone,SSN
John Doe,john@email.com,(555) 123-4567,123-45-6789
Jane Smith,jane@email.com,(555) 987-6543,987-65-4321"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except:
        pass

@pytest.fixture
def temp_json_file():
    """Create temporary JSON file with PII"""
    import json
    
    data = {
        "users": [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "(555) 123-4567",
                "ssn": "123-45-6789"
            },
            {
                "name": "Jane Smith", 
                "contact": {
                    "email": "jane@example.com",
                    "phone": "555-987-6543"
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except:
        pass