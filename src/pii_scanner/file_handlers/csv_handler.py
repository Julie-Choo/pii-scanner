# src/pii_scanner/file_handlers/csv_handler.py
"""
Handler for CSV files
"""

import time
import pandas as pd
from .base import BaseFileHandler
from ..core.models import FileInfo, ScanResult, ScanOptions, PIIMatch
from ..exceptions import FileHandlerError
from ..utils.logger import get_logger
from typing import List

logger = get_logger(__name__)

class CSVFileHandler(BaseFileHandler):
    """Handler for CSV files"""
    
    SUPPORTED_EXTENSIONS = ['.csv']
    
    def can_handle(self, file_info: FileInfo) -> bool:
        """Check if file is CSV"""
        return file_info.extension in self.SUPPORTED_EXTENSIONS
    
    def scan_file(self, file_info: FileInfo, options: ScanOptions) -> ScanResult:
        """Scan CSV file for PII"""
        start_time = time.time()
        all_matches = []
        
        try:
            # Read CSV with pandas
            df = self._read_csv_safely(file_info.path)
            
            # Scan each cell
            for row_idx, row in df.iterrows():
                for col_name, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        # Scan cell content
                        cell_result = self.scanner.scan_text(str(value), options)
                        
                        # Update match locations
                        for match in cell_result.matches:
                            match.location = f"File: {file_info.name}, Row: {row_idx + 2}, Column: {col_name}"
                            # Add original cell location to context
                            if match.context:
                                match.context = f"[{col_name}: {row_idx + 2}] {match.context}"
                        
                        all_matches.extend(cell_result.matches)
            
            # Also scan column headers
            headers_text = " ".join(str(col) for col in df.columns)
            header_result = self.scanner.scan_text(headers_text, options)
            
            for match in header_result.matches:
                match.location = f"File: {file_info.name}, Headers"
            
            all_matches.extend(header_result.matches)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ScanResult(
                matches=all_matches,
                processing_time_ms=processing_time,
                source_info={
                    "type": "csv_file",
                    "file_name": file_info.name,
                    "file_path": file_info.path,
                    "file_size": file_info.size_bytes,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns)
                }
            )
            
        except Exception as e:
            logger.error(f"Error scanning CSV file {file_info.path}: {e}")
            raise FileHandlerError(f"Failed to scan CSV file: {e}")
    
    def _read_csv_safely(self, file_path: str) -> pd.DataFrame:
        """Read CSV file with error handling and encoding detection"""
        # Try common separators
        separators = [',', ';', '\t', '|']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=sep,
                        dtype=str,  # Read all as strings
                        encoding=encoding,
                        on_bad_lines='skip'  # Skip problematic lines
                    )
                    
                    # Check if we found a good separator (more than 1 column)
                    if len(df.columns) > 1:
                        logger.debug(f"Successfully read CSV with separator '{sep}' and encoding '{encoding}'")
                        return df
                        
                except Exception as e:
                    logger.debug(f"Failed to read CSV with sep='{sep}', encoding='{encoding}': {e}")
                    continue
        
        # Fallback to default pandas behavior
        try:
            return pd.read_csv(file_path, dtype=str, on_bad_lines='skip')
        except Exception as e:
            raise FileHandlerError(f"Could not read CSV file with any encoding/separator: {e}")
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported extensions"""
        return self.SUPPORTED_EXTENSIONS