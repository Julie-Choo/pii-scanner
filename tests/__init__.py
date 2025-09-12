from .utils.config import get_config
from .utils.logger import get_logger, setup_logging
from .core.scanner import PIIScanner, get_scanner, scan_text, anonymize_text
from .core.models import PIIMatch, ScanResult, ScanOptions, EntityType, ConfidenceLevel, FileInfo
from .core.anonymizer import PIIAnonymizer
from .file_handlers.factory import FileHandlerFactory
from .exceptions import PIIScannerError, ScannerError, FileHandlerError

__version__ = "1.0.0"
__all__ = ["PIIScanner", "get_scanner", "scan_text", "anonymize_text", "PIIMatch", "ScanResult", "ScanOptions", "EntityType", "ConfidenceLevel", "FileInfo", "PIIAnonymizer", "FileHandlerFactory", "get_config", "get_logger", "setup_logging", "PIIScannerError", "ScannerError", "FileHandlerError"]

try:
    setup_logging()
except:
    pass