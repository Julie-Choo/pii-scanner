# tests/test_file_handlers/test_csv_handler.py
"""
Test CSV file handler
"""

import pytest
from pii_scanner.file_handlers.csv_handler import CSVFileHandler
from pii_scanner.core.models import FileInfo, ScanOptions

class TestCSVFileHandler:
    """Test CSV file handler"""
    
    @pytest.fixture
    def handler(self, scanner):
        return CSVFileHandler(scanner)
    
    def test_can_handle_csv(self, handler):
        """Test handler recognizes CSV files"""
        file_info = FileInfo(path="test.csv", name="test.csv", 
                           extension=".csv", size_bytes=100)
        assert handler.can_handle(file_info)
    
    def test_scan_csv_file(self, handler, temp_csv_file, scan_options):
        """Test scanning CSV file"""
        file_info = FileInfo.from_path(temp_csv_file)
        result = handler.scan_file(file_info, scan_options)
        
        assert result is not None
        assert result.total_entities >= 4  # Should find multiple PII entities
        
        # Check that results have proper location info
        for match in result.matches:
            assert "Row:" in match.location or "Headers" in match.location
            assert "Column:" in match.location or "Headers" in match.location
        
        # Check source info
        assert result.source_info["type"] == "csv_file"
        assert result.source_info["rows"] >= 2
        assert result.source_info["columns"] >= 3