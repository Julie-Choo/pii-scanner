# src/pii_scanner/file_handlers/__init__.py
"""
File handlers for different file types
"""

from .base import BaseFileHandler
from .text_handler import TextFileHandler
from .csv_handler import CSVFileHandler
from .json_handler import JSONFileHandler
from .factory import FileHandlerFactory

__all__ = [
    'BaseFileHandler',
    'TextFileHandler', 
    'CSVFileHandler',
    'JSONFileHandler',
    'FileHandlerFactory'
]