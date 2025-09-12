# tests/test_core/test_scanner.py
"""
Test core scanner functionality
"""

import pytest
from pii_scanner import PIIScanner, ScanOptions, EntityType
from pii_scanner.exceptions import ScannerError, InitializationError

class TestPIIScanner:
    """Test PII scanner core functionality"""
    
    def test_scanner_initialization(self, scanner):
        """Test scanner initializes correctly"""
        assert scanner is not None
        assert scanner.is_ready()
        
    def test_health_check(self, scanner):
        """Test scanner health check"""
        health = scanner.health_check()
        assert health["status"] == "healthy"
        assert health["initialized"] is True
        assert health["analyzer_ready"] is True
        assert health["anonymizer_ready"] is True
        
    def test_get_supported_entities(self, scanner):
        """Test getting supported entities"""
        entities = scanner.get_supported_entities()
        assert isinstance(entities, list)
        assert len(entities) > 0
        assert "EMAIL_ADDRESS" in entities
        assert "PHONE_NUMBER" in entities
        assert "US_SSN" in entities
    
    def test_scan_empty_text(self, scanner):
        """Test scanning empty text"""
        result = scanner.scan_text("")
        assert result.total_entities == 0
        assert len(result.matches) == 0
        
    def test_scan_no_pii_text(self, scanner):
        """Test scanning text with no PII"""
        text = "This is a simple sentence with no personal information."
        result = scanner.scan_text(text)
        assert result.total_entities == 0
        assert len(result.matches) == 0
    
    def test_scan_email(self, scanner):
        """Test email detection"""
        text = "Contact me at john.doe@company.com for more information."
        result = scanner.scan_text(text)
        
        assert result.total_entities >= 1
        email_matches = [m for m in result.matches if m.entity_type == "EMAIL_ADDRESS"]
        assert len(email_matches) >= 1
        assert "john.doe@company.com" in [m.text for m in email_matches]
        
    def test_scan_phone(self, scanner):
        """Test phone number detection"""
        text = "Call me at (555) 123-4567 or text 555-987-6543."
        result = scanner.scan_text(text)
        
        phone_matches = [m for m in result.matches if m.entity_type == "PHONE_NUMBER"]
        assert len(phone_matches) >= 1
        
    def test_scan_ssn(self, scanner):
        """Test SSN detection"""
        text = "My SSN is 123-45-6789 for verification purposes."
        result = scanner.scan_text(text)
        
        ssn_matches = [m for m in result.matches if "SSN" in m.entity_type]
        assert len(ssn_matches) >= 1
        
    def test_scan_multiple_entities(self, scanner, sample_pii_text):
        """Test scanning text with multiple PII types"""
        result = scanner.scan_text(sample_pii_text)
        
        assert result.total_entities >= 3  # Should find multiple entities
        
        # Check entity distribution
        entity_counts = result.entity_counts
        assert len(entity_counts) >= 3  # Multiple entity types
        
        # Check confidence distribution
        conf_dist = result.confidence_distribution
        assert sum(conf_dist.values()) == result.total_entities
    
    def test_confidence_threshold(self, scanner, sample_pii_text):
        """Test confidence threshold filtering"""
        # High confidence threshold
        high_options = ScanOptions(confidence_threshold=0.9)
        high_result = scanner.scan_text(sample_pii_text, high_options)
        
        # Low confidence threshold
        low_options = ScanOptions(confidence_threshold=0.1)
        low_result = scanner.scan_text(sample_pii_text, low_options)
        
        # Should find more entities with lower threshold
        assert low_result.total_entities >= high_result.total_entities
        
        # All high confidence results should have confidence >= 0.9
        for match in high_result.matches:
            assert match.confidence >= 0.9
    
    def test_entity_type_filtering(self, scanner, sample_pii_text):
        """Test filtering by entity types"""
        # Only scan for emails
        email_options = ScanOptions(entity_types=["EMAIL_ADDRESS"])
        email_result = scanner.scan_text(sample_pii_text, email_options)
        
        for match in email_result.matches:
            assert match.entity_type == "EMAIL_ADDRESS"
    
    def test_context_extraction(self, scanner):
        """Test context extraction around PII"""
        text = "The customer's email address is john.doe@company.com and should be kept confidential."
        
        options = ScanOptions(include_context=True, context_window=20)
        result = scanner.scan_text(text, options)
        
        email_matches = [m for m in result.matches if m.entity_type == "EMAIL_ADDRESS"]
        assert len(email_matches) >= 1
        
        email_match = email_matches[0]
        assert email_match.context
        assert "email address" in email_match.context.lower()
    
    def test_anonymization(self, scanner, sample_pii_text):
        """Test text anonymization"""
        anonymized = scanner.anonymize_text(sample_pii_text)
        
        assert anonymized != sample_pii_text
        assert len(anonymized) > 0
        
        # Original PII should not be in anonymized text
        assert "john.doe@company.com" not in anonymized
        assert "123-45-6789" not in anonymized
        assert "(555) 123-4567" not in anonymized

class TestScanOptions:
    """Test ScanOptions configuration"""
    
    def test_default_options(self):
        """Test default scan options"""
        options = ScanOptions()
        
        assert options.confidence_threshold == 0.5
        assert options.include_context is True
        assert options.context_window == 50
        assert options.anonymize_results is True
        assert options.language == "en"
        assert options.entity_types is not None
        assert len(options.entity_types) > 0
    
    def test_invalid_confidence_threshold(self):
        """Test invalid confidence threshold"""
        with pytest.raises(ValueError):
            ScanOptions(confidence_threshold=-0.1)
            
        with pytest.raises(ValueError):
            ScanOptions(confidence_threshold=1.1)
    
    def test_invalid_context_window(self):
        """Test invalid context window"""
        with pytest.raises(ValueError):
            ScanOptions(context_window=-1)