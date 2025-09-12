# docs/API.md
# API Reference

## Core Scanner

### `PIIScanner`

Main scanner class for PII detection and anonymization.

#### Methods

##### `scan_text(text: str, options: ScanOptions = None) -> ScanResult`

Scan text for PII entities.

**Parameters:**
- `text`: Text to scan
- `options`: Scanning options (optional)

**Returns:** `ScanResult` containing detected PII entities

**Example:**
```python
from pii_scanner import PIIScanner, ScanOptions

scanner = PIIScanner()
options = ScanOptions(confidence_threshold=0.8)
result = scanner.scan_text("Email: john@example.com", options)
```

##### `anonymize_text(text: str, options: ScanOptions = None) -> str`

Anonymize PII in text.

**Parameters:**
- `text`: Text to anonymize
- `options`: Scanning options (optional)

**Returns:** Anonymized text string

## Data Models

### `PIIMatch`

Represents a detected PII entity.

**Attributes:**
- `entity_type: str` - Type of PII (e.g., "EMAIL_ADDRESS")
- `text: str` - Original text containing PII
- `start: int` - Start position in text
- `end: int` - End position in text
- `confidence: float` - Detection confidence (0.0-1.0)
- `location: str` - Location where PII was found
- `context: str` - Surrounding context
- `anonymized_text: str` - Anonymized version

### `ScanResult`

Results of a PII scan operation.

**Attributes:**
- `matches: List[PIIMatch]` - Detected PII entities
- `total_entities: int` - Total number of entities found
- `processing_time_ms: float` - Processing time
- `source_info: Dict` - Information about scanned source

**Methods:**
- `get_summary() -> Dict` - Get scan summary statistics
- `to_dict() -> Dict` - Convert to dictionary

### `ScanOptions`

Configuration for scanning operations.

**Attributes:**
- `confidence_threshold: float = 0.5` - Minimum confidence
- `entity_types: List[str] = None` - Entity types to detect
- `include_context: bool = True` - Include context around PII
- `context_window: int = 50` - Context window size
- `anonymize_results: bool = True` - Anonymize detected PII

## File Handlers

### `FileHandlerFactory`

Factory for creating file handlers.

#### Methods

##### `get_handler(file_info: FileInfo) -> BaseFileHandler`

Get appropriate handler for file type.

##### `get_supported_extensions() -> List[str]`

Get list of supported file extensions.

### `BaseFileHandler`

Abstract base class for file handlers.

#### Methods

##### `can_handle(file_info: FileInfo) -> bool`

Check if handler supports file type.

##### `scan_file(file_info: FileInfo, options: ScanOptions) -> ScanResult`

Scan file for PII entities.

## REST API Endpoints

### Health Endpoints

#### `GET /health/`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "scanner_ready": true,
  "supported_entities": ["EMAIL_ADDRESS", "PHONE_NUMBER", ...],
  "version": "1.0.0"
}
```

### Scanning Endpoints

#### `POST /scan/text`

Scan text for PII.

**Request Body:**
```json
{
  "text": "Contact john@example.com",
  "confidence_threshold": 0.5,
  "entity_types": ["EMAIL_ADDRESS"],
  "include_context": true,
  "context_window": 50
}
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_entities": 1,
    "entity_counts": {"EMAIL_ADDRESS": 1},
    "confidence_distribution": {"high": 1, "medium": 0, "low": 0},
    "average_confidence": 0.95,
    "processing_time_ms": 25.5
  },
  "matches": [
    {
      "entity_type": "EMAIL_ADDRESS",
      "text": "john@example.com",
      "start": 8,
      "end": 24,
      "confidence": 0.95,
      "confidence_level": "high",
      "location": "text input",
      "context": "Contact john@example.com for info",
      "anonymized_text": "jo***@example.com",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "source_info": {
    "type": "text",
    "length": 24,
    "confidence_threshold": 0.5
  }
}
```

#### `POST /scan/file`

Scan uploaded file for PII.

**Request:** Multipart form with file upload

**Response:** Same format as text scanning

### Anonymization Endpoints

#### `POST /anonymize/text`

Anonymize PII in text.

**Request Body:**
```json
{
  "text": "Call me at (555) 123-4567",
  "confidence_threshold": 0.5,
  "entity_types": ["PHONE_NUMBER"]
}
```

**Response:**
```json
{
  "success": true,
  "original_text": "Call me at (555) 123-4567",
  "anonymized_text": "Call me at ***-***-4567",
  "entities_anonymized": 1,
  "processing_time_ms": 15.2
}
```

## Configuration

Configuration is loaded from YAML files and environment variables.

### Configuration Structure

```yaml
scanner:
  confidence_threshold: 0.5
  context_window: 50
  default_entities:
    - EMAIL_ADDRESS
    - PHONE_NUMBER
    - US_SSN
  language: en

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

api:
  host: 0.0.0.0
  port: 8000
  cors_enabled: true

streamlit:
  host: 0.0.0.0
  port: 8501
```

### Environment Variables

- `PII_CONFIDENCE_THRESHOLD` - Override confidence threshold
- `LOG_LEVEL` - Set logging level
- `API_HOST` - API host address
- `API_PORT` - API port number

---

# docs/USAGE.md
# Usage Guide

## Basic Text Scanning

### Simple Text Scanning

```python
from pii_scanner import scan_text

# Basic scanning
text = "Contact John Doe at john.doe@company.com"
result = scan_text(text)

print(f"Found {result.total_entities} PII entities")
for match in result.matches:
    print(f"  {match.entity_type}: {match.text} → {match.anonymized_text}")
```

### Advanced Text Scanning

```python
from pii_scanner import PIIScanner, ScanOptions

scanner = PIIScanner()

# Configure scanning options
options = ScanOptions(
    confidence_threshold=0.8,           # Higher confidence
    entity_types=["EMAIL_ADDRESS", "PHONE_NUMBER"],  # Specific types
    include_context=True,               # Include context
    context_window=100                  # Larger context window
)

result = scanner.scan_text(text, options)

# Access detailed results
summary = result.get_summary()
print(f"Processing time: {summary['processing_time_ms']:.1f}ms")
print(f"Average confidence: {summary['average_confidence']:.1%}")
```

## File Scanning

### Scanning Individual Files

```python
from pii_scanner import get_scanner
from pii_scanner.file_handlers import FileHandlerFactory
from pii_scanner.core.models import FileInfo, ScanOptions

scanner = get_scanner()
file_factory = FileHandlerFactory(scanner)

# Scan a CSV file
file_info = FileInfo.from_path("customer_data.csv")
handler = file_factory.get_handler(file_info)

options = ScanOptions(confidence_threshold=0.6)
result = handler.scan_file(file_info, options)

print(f"Found {result.total_entities} PII entities in {file_info.name}")
```

### Batch File Scanning

```python
import os
from pathlib import Path

def scan_directory(directory_path: str):
    """Scan all supported files in a directory"""
    results = {}
    
    for file_path in Path(directory_path).rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.txt', '.csv', '.json']:
            try:
                file_info = FileInfo.from_path(str(file_path))
                handler = file_factory.get_handler(file_info)
                result = handler.scan_file(file_info, ScanOptions())
                
                if result.matches:
                    results[str(file_path)] = result
                    
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
    
    return results

# Scan directory
directory_results = scan_directory("./data")
print(f"Found PII in {len(directory_results)} files")
```

## Text Anonymization

### Basic Anonymization

```python
from pii_scanner import anonymize_text

text = "John's SSN is 123-45-6789 and email is john@company.com"
anonymized = anonymize_text(text)
print(anonymized)
# Output: "John's SSN is ***-**-6789 and email is jo***@company.com"
```

### Custom Anonymization

```python
from pii_scanner.core.anonymizer import PIIAnonymizer

anonymizer = PIIAnonymizer()

# Consistent masking (same input = same output)
email = "john.doe@company.com"
masked1 = anonymizer.generate_consistent_mask(email, "EMAIL_ADDRESS")
masked2 = anonymizer.generate_consistent_mask(email, "EMAIL_ADDRESS")
assert masked1 == masked2  # True

print(masked1)  # user_a1b2c3d4@example.com
```

## Working with Different File Types

### CSV Files

```python
import pandas as pd
from pii_scanner.file_handlers.csv_handler import CSVFileHandler

# The CSV handler automatically:
# 1. Detects file encoding
# 2. Tries different separators (,;|\t)
# 3. Scans each cell for PII
# 4. Includes row/column location info

handler = CSVFileHandler(scanner)
result = handler.scan_file(file_info, options)

# Results include location like:
# "File: data.csv, Row: 5, Column: email"
```

### JSON Files

```python
from pii_scanner.file_handlers.json_handler import JSONFileHandler

# JSON handler recursively scans:
# 1. Object properties
# 2. Array elements  
# 3. Nested structures
# 4. String values only

handler = JSONFileHandler(scanner)
result = handler.scan_file(file_info, options)

# Results include JSON path like:
# "File: data.json, Path: users[0].contact.email"
```

## Configuration

### Using Configuration Files

```python
from pii_scanner.utils.config import get_config

# Load configuration
config = get_config("config/production.yaml")

# Access configuration values
threshold = config.get("scanner", "confidence_threshold")
entities = config.get("scanner", "default_entities")
```

### Environment Variables

```bash
# Set environment variables
export PII_CONFIDENCE_THRESHOLD=0.7
export LOG_LEVEL=DEBUG
export API_PORT=9000

# These override config file values
```

## Error Handling

```python
from pii_scanner.exceptions import (
    ScannerError, 
    FileHandlerError, 
    UnsupportedFileTypeError,
    ValidationError
)

try:
    result = scanner.scan_text(text)
except ScannerError as e:
    print(f"Scanner error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    handler = file_factory.get_handler(file_info)
except UnsupportedFileTypeError as e:
    print(f"Unsupported file type: {e}")
```

## Performance Optimization

### Batch Processing

```python
# For large datasets, process in batches
def process_large_dataset(texts: List[str], batch_size: int = 100):
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        for text in batch:
            result = scanner.scan_text(text)
            results.append(result)
    
    return results
```

### Caching Results

```python
import hashlib
import pickle

def cached_scan(text: str, cache_dir: str = "cache/"):
    """Cache scan results to avoid re-processing"""
    
    # Create cache key
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{text_hash}.pkl")
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Scan and cache
    result = scanner.scan_text(text)
    
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)
    
    return result
```

## Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
from pii_scanner import get_scanner

app = Flask(__name__)
scanner = get_scanner()

@app.route('/scan', methods=['POST'])
def scan_endpoint():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = scanner.scan_text(text)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pii_scanner import get_scanner

scanner = get_scanner()

@csrf_exempt
def scan_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')
        
        result = scanner.scan_text(text)
        return JsonResponse(result.to_dict())
```
