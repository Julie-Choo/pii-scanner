# src/pii_scanner/file_handlers/factory.py
"""
File handler factory
"""

from typing import List, Optional
from .base import BaseFileHandler
from .text_handler import TextFileHandler
from .csv_handler import CSVFileHandler
from .json_handler import JSONFileHandler
from ..core.models import FileInfo
from ..exceptions import UnsupportedFileTypeError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class FileHandlerFactory:
    """Factory for creating appropriate file handlers"""
    
    def __init__(self, scanner):
        """Initialize factory with scanner instance"""
        self.scanner = scanner
        self.handlers = [
            TextFileHandler(scanner),
            CSVFileHandler(scanner),
            JSONFileHandler(scanner)
        ]
    
    def get_handler(self, file_info: FileInfo) -> BaseFileHandler:
        """Get appropriate handler for file type"""
        for handler in self.handlers:
            if handler.can_handle(file_info):
                logger.debug(f"Selected {handler.__class__.__name__} for {file_info.name}")
                return handler
        
        raise UnsupportedFileTypeError(
            f"No handler found for file type: {file_info.extension}. "
            f"Supported types: {self.get_supported_extensions()}"
        )
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        extensions = []
        for handler in self.handlers:
            extensions.extend(handler.get_supported_extensions())
        return sorted(list(set(extensions)))
    
    def add_handler(self, handler: BaseFileHandler):
        """Add a custom file handler"""
        self.handlers.append(handler)
        logger.info(f"Added custom handler: {handler.__class__.__name__}")