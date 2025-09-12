# src/pii_scanner/__init__.py
"""
PII Scanner Package
Simple, modular PII detection and anonymization using Microsoft Presidio
"""

from .core.scanner import PIIScanner, get_scanner, scan_text, anonymize_text
from .core.models import PIIMatch, ScanResult, ScanOptions, EntityType, ConfidenceLevel
from .core.anonymizer import PIIAnonymizer
from .file_handlers import FileHandlerFactory
from .utils.config import get_config
from .utils.logger import get_logger, setup_logging
from .exceptions import PIIScannerError, ScannerError, FileHandlerError

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
    "FileHandlerError"
]

# Initialize logging when package is imported
setup_logging()