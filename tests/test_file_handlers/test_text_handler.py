# tests/test_file_handlers/test_text_handler.py
"""
Test text file handler
"""

import pytest
import tempfile
import os
from pii_scanner.file_handlers.text_handler import TextFileHandler
from pii_scanner.core.models import FileInfo, ScanOptions

class TestTextFileHandler:
    """Test text file handler"""
    
    @pytest.fixture
    def handler(self, scanner):
        return TextFileHandler(scanner)
    
    def test_can_handle_supported_extensions(self, handler):
        """Test handler recognizes supported extensions"""
        for ext in ['.txt', '.log', '.md', '.py']:
            file_info = FileInfo(path=f"test{ext}", name=f"test{ext}", 
                               extension=ext, size_bytes=100)
            assert handler.can_handle(file_info)
    
    def test_cannot_handle_unsupported_extensions(self, handler):
        """Test handler rejects unsupported extensions"""
        file_info = FileInfo(path="test.pdf", name="test.pdf", 
                           extension=".pdf", size_bytes=100)
        assert not handler.can_handle(file_info)
    
    def test_scan_text_file(self, handler, temp_text_file, scan_options):
        """Test scanning text file"""
        file_info = FileInfo.from_path(temp_text_file)
        result = handler.scan_file(file_info, scan_options)
        
        assert result is not None
        assert result.total_entities >= 1  # Should find email and phone
        assert result.processing_time_ms > 0
        
        # Check source info
        assert result.source_info["type"] == "text_file"
        assert result.source_info["file_name"] == os.path.basename(temp_text_file)
    
    def test_get_supported_extensions(self, handler):
        """Test getting supported extensions"""
        extensions = handler.get_supported_extensions()
        assert isinstance(extensions, list)
        assert '.txt' in extensions
        assert '.log' in extensions