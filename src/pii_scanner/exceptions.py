# src/pii_scanner/exceptions.py
"""
Custom exceptions for PII scanner
"""

class PIIScannerError(Exception):
    """Base exception for PII scanner"""
    pass

class InitializationError(PIIScannerError):
    """Raised when scanner fails to initialize"""
    pass

class ScannerError(PIIScannerError):
    """Raised when scanning operation fails"""
    pass

class FileHandlerError(PIIScannerError):
    """Raised when file handling fails"""
    pass

class UnsupportedFileTypeError(FileHandlerError):
    """Raised when file type is not supported"""
    pass

class ValidationError(PIIScannerError):
    """Raised when input validation fails"""
    pass

class AnonymizationError(PIIScannerError):
    """Raised when anonymization fails"""
    pass

class ConfigurationError(PIIScannerError):
    """Raised when configuration is invalid"""
    pass