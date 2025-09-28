"""
Base file handler interface
"""

from abc import ABC, abstractmethod
from typing import List
from ..core.models import PIIMatch, ScanResult, ScanOptions, FileInfo
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BaseFileHandler(ABC):
    """Abstract base class for file handlers"""
    
    def __init__(self, scanner):
        """Initialize with scanner instance"""
        self.scanner = scanner
    
    @abstractmethod
    def can_handle(self, file_info: FileInfo) -> bool:
        """Check if this handler can process the file type"""
        pass
    
    @abstractmethod
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        """Scan file for PII entities"""
        pass
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return []