# src/pii_scanner/__init__.py
"""
PII Scanner Package
Simple, modular PII detection and anonymization using Microsoft Presidio
"""

# Import utilities first (no circular dependency)
from .utils.config import get_config
from .utils.logger import get_logger, setup_logging

# Import core components
from .core.scanner import PIIScanner, get_scanner, scan_text, anonymize_text
from .core.models import PIIMatch, ScanResult, ScanOptions, EntityType, ConfidenceLevel, FileInfo
from .core.anonymizer import PIIAnonymizer

# Import file handlers
from .file_handlers.factory import FileHandlerFactory

# Import exceptions
from .exceptions import (
    PIIScannerError, 
    ScannerError, 
    FileHandlerError, 
    UnsupportedFileTypeError,
    ValidationError,
    InitializationError
)

__version__ = "1.0.0"

__all__ = [
    # Core functionality
    "PIIScanner",
    "get_scanner", 
    "scan_text",
    "anonymize_text",
    
    # Models
    "PIIMatch",
    "ScanResult", 
    "ScanOptions",
    "EntityType",
    "ConfidenceLevel",
    "FileInfo",
    
    # Components
    "PIIAnonymizer",
    "FileHandlerFactory",
    
    # Utilities
    "get_config",
    "get_logger",
    "setup_logging",
    
    # Exceptions
    "PIIScannerError",
    "ScannerError", 
    "FileHandlerError",
    "UnsupportedFileTypeError",
    "ValidationError",
    "InitializationError"
]

# Initialize logging when package is imported (safe now)
try:
    setup_logging()
except Exception:
    # If logging setup fails, continue anyway
    pass
