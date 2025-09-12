# tests/test_file_handlers/test_json_handler.py
"""
Test JSON file handler
"""

import pytest
from pii_scanner.file_handlers.json_handler import JSONFileHandler
from pii_scanner.core.models import FileInfo, ScanOptions

class TestJSONFileHandler:
    """Test JSON file handler"""
    
    @pytest.fixture
    def handler(self, scanner):
        return JSONFileHandler(scanner)
    
    def test_can_handle_json(self, handler):
        """Test handler recognizes JSON files"""
        file_info = FileInfo(path="test.json", name="test.json", 
                           extension=".json", size_bytes=100)
        assert handler.can_handle(file_info)
    
    def test_scan_json_file(self, handler, temp_json_file, scan_options):
        """Test scanning JSON file"""
        file_info = FileInfo.from_path(temp_json_file)
        result = handler.scan_file(file_info, scan_options)
        
        assert result is not None
        assert result.total_entities >= 3  # Should find emails, phones, SSN
        
        # Check that results have proper location info
        for match in result.matches:
            assert "Path:" in match.location
        
        # Check source info
        assert result.source_info["type"] == "json_file"