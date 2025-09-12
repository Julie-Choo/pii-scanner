# tests/test_core/test_models.py
"""
Test data models
"""

import pytest
from datetime import datetime
from pii_scanner.core.models import PIIMatch, ScanResult, ScanOptions, ConfidenceLevel, EntityType

class TestPIIMatch:
    """Test PIIMatch model"""
    
    def test_create_pii_match(self):
        """Test creating PIIMatch instance"""
        match = PIIMatch(
            entity_type="EMAIL_ADDRESS",
            text="john@example.com",
            start=0,
            end=16,
            confidence=0.95,
            location="test file",
            context="Contact john@example.com",
            anonymized_text="jo***@example.com"
        )
        
        assert match.entity_type == "EMAIL_ADDRESS"
        assert match.text == "john@example.com"
        assert match.confidence == 0.95
        assert match.confidence_level == ConfidenceLevel.HIGH
    
    def test_confidence_levels(self):
        """Test confidence level categorization"""
        high_match = PIIMatch("EMAIL", "test", 0, 4, 0.9, "", "", "")
        assert high_match.confidence_level == ConfidenceLevel.HIGH
        
        medium_match = PIIMatch("EMAIL", "test", 0, 4, 0.7, "", "", "")
        assert medium_match.confidence_level == ConfidenceLevel.MEDIUM
        
        low_match = PIIMatch("EMAIL", "test", 0, 4, 0.4, "", "", "")
        assert low_match.confidence_level == ConfidenceLevel.LOW
    
    def test_to_dict(self):
        """Test converting PIIMatch to dictionary"""
        match = PIIMatch("EMAIL", "test@example.com", 0, 16, 0.8, "file", "context", "masked")
        result_dict = match.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["entity_type"] == "EMAIL"
        assert result_dict["confidence"] == 0.8
        assert result_dict["confidence_level"] == "high"

class TestScanResult:
    """Test ScanResult model"""
    
    def test_create_empty_scan_result(self):
        """Test creating empty scan result"""
        result = ScanResult()
        
        assert result.total_entities == 0
        assert len(result.matches) == 0
        assert result.entity_counts == {}
        assert result.average_confidence == 0.0
    
    def test_scan_result_with_matches(self):
        """Test scan result with matches"""
        matches = [
            PIIMatch("EMAIL", "john@test.com", 0, 13, 0.9, "", "", ""),
            PIIMatch("PHONE", "555-1234", 14, 22, 0.8, "", "", ""),
            PIIMatch("EMAIL", "jane@test.com", 23, 36, 0.85, "", "", "")
        ]
        
        result = ScanResult(matches=matches)
        
        assert result.total_entities == 3
        assert len(result.matches) == 3
        
        # Test entity counts
        entity_counts = result.entity_counts
        assert entity_counts["EMAIL"] == 2
        assert entity_counts["PHONE"] == 1
        
        # Test average confidence
        expected_avg = (0.9 + 0.8 + 0.85) / 3
        assert abs(result.average_confidence - expected_avg) < 0.01
        
        # Test confidence distribution
        conf_dist = result.confidence_distribution
        assert conf_dist["high"] == 2  # 0.9 and 0.85
        assert conf_dist["medium"] == 1  # 0.8
        assert conf_dist["low"] == 0
    
    def test_get_summary(self):
        """Test getting scan summary"""
        matches = [PIIMatch("EMAIL", "test", 0, 4, 0.9, "", "", "")]
        result = ScanResult(matches=matches, processing_time_ms=100.0)
        
        summary = result.get_summary()
        
        assert summary["total_entities"] == 1
        assert summary["processing_time_ms"] == 100.0
        assert "entity_counts" in summary
        assert "confidence_distribution" in summary