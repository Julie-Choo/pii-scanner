"""
Handler for plain text files
"""

import time
from .base import BaseFileHandler
from ..core.models import FileInfo, ScanResult, ScanOptions
from ..exceptions import FileHandlerError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TextFileHandler(BaseFileHandler):
    """Handler for plain text files (.txt, .log, .md)"""
    
    SUPPORTED_EXTENSIONS = ['.txt', '.log', '.md', '.py', '.js', '.html', '.css']
    
    def can_handle(self, file_info: FileInfo) -> bool:
        """Check if file extension is supported"""
        return file_info.extension in self.SUPPORTED_EXTENSIONS
    
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        """Scan text file for PII"""
        start_time = time.time()
        
        try:
            # Detect encoding
            encoding = self._detect_encoding(file_info.path)
            
            # Read file content
            with open(file_info.path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            # Scan content using core scanner
            text_result = self.scanner.scan_text(content, options)
            
            # Update match locations to include file reference
            for match in text_result.matches:
                match.location = f"File: {file_info.name}, Position: {match.start}-{match.end}"
            
            # Update source info
            processing_time = (time.time() - start_time) * 1000
            
            return ScanResult(
                matches=text_result.matches,
                processing_time_ms=processing_time,
                source_info={
                    "type": "text_file",
                    "file_name": file_info.name,
                    "file_path": file_info.path,
                    "file_size": file_info.size_bytes,
                    "encoding": encoding,
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            logger.error(f"Error scanning text file {file_info.path}: {e}")
            raise FileHandlerError(f"Failed to scan text file: {e}")
    
    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except ImportError:
            return 'utf-8'  # Default fallback
        except Exception as e:
            logger.warning(f"Encoding detection failed for {file_path}: {e}")
            return 'utf-8'
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported extensions"""
        return self.SUPPORTED_EXTENSIONS