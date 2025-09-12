# src/pii_scanner/file_handlers/json_handler.py
"""
Handler for JSON files
"""

import json
import time
from .base import BaseFileHandler
from ..core.models import FileInfo, ScanResult, ScanOptions
from ..exceptions import FileHandlerError
from ..utils.logger import get_logger
from typing import List

logger = get_logger(__name__)

class JSONFileHandler(BaseFileHandler):
    """Handler for JSON files"""
    
    SUPPORTED_EXTENSIONS = ['.json']
    
    def can_handle(self, file_info: FileInfo) -> bool:
        """Check if file is JSON"""
        return file_info.extension in self.SUPPORTED_EXTENSIONS
    
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        """Scan JSON file for PII"""
        start_time = time.time()
        all_matches = []
        
        try:
            # Read JSON file
            with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            # Recursively scan JSON structure
            self._scan_json_recursive(data, all_matches, file_info.name, options)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ScanResult(
                matches=all_matches,
                processing_time_ms=processing_time,
                source_info={
                    "type": "json_file",
                    "file_name": file_info.name,
                    "file_path": file_info.path,
                    "file_size": file_info.size_bytes,
                    "structure_type": type(data).__name__
                }
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_info.path}: {e}")
            raise FileHandlerError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error scanning JSON file {file_info.path}: {e}")
            raise FileHandlerError(f"Failed to scan JSON file: {e}")
    
    def _scan_json_recursive(self, obj, matches_list, file_name, options, path=""):
        """Recursively scan JSON object structure"""
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                self._scan_json_recursive(value, matches_list, file_name, options, current_path)
                
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                current_path = f"{path}[{idx}]"
                self._scan_json_recursive(item, matches_list, file_name, options, current_path)
                
        elif isinstance(obj, str) and obj.strip():
            # Scan string values for PII
            text_result = self.scanner.scan_text(obj, options)
            
            # Update match locations
            for match in text_result.matches:
                match.location = f"File: {file_name}, Path: {path}"
                if match.context:
                    match.context = f"[JSON:{path}] {match.context}"
            
            matches_list.extend(text_result.matches)
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported extensions"""
        return self.SUPPORTED_EXTENSIONS