# tests/test_core/test_anonymizer.py
"""
Test anonymizer functionality
"""

import pytest
from pii_scanner.core.anonymizer import PIIAnonymizer

class TestPIIAnonymizer:
    """Test PII anonymizer"""
    
    @pytest.fixture
    def anonymizer(self):
        return PIIAnonymizer()
    
    def test_email_anonymization(self, anonymizer):
        """Test email anonymization"""
        email = "john.doe@company.com"
        anonymized = anonymizer.anonymize_entity(email, "EMAIL_ADDRESS")
        
        assert anonymized != email
        assert "@company.com" in anonymized
        assert "jo" in anonymized  # First two chars preserved
        assert "john.doe" not in anonymized
    
    def test_phone_anonymization(self, anonymizer):
        """Test phone number anonymization"""
        phone = "(555) 123-4567"
        anonymized = anonymizer.anonymize_entity(phone, "PHONE_NUMBER")
        
        assert anonymized != phone
        assert "4567" in anonymized  # Last 4 digits preserved
        assert "***-***-" in anonymized
    
    def test_ssn_anonymization(self, anonymizer):
        """Test SSN anonymization"""
        ssn = "123-45-6789"
        anonymized = anonymizer.anonymize_entity(ssn, "US_SSN")
        
        assert anonymized != ssn
        assert "6789" in anonymized  # Last 4 digits preserved
        assert "***-**-" in anonymized
    
    def test_credit_card_anonymization(self, anonymizer):
        """Test credit card anonymization"""
        cc = "4532-1234-5678-9012"
        anonymized = anonymizer.anonymize_entity(cc, "CREDIT_CARD")
        
        assert anonymized != cc
        assert "9012" in anonymized  # Last 4 digits preserved
        assert "****-****-****-" in anonymized
    
    def test_person_name_anonymization(self, anonymizer):
        """Test person name anonymization"""
        name = "John Doe"
        anonymized = anonymizer.anonymize_entity(name, "PERSON")
        
        assert anonymized != name
        assert "J***" in anonymized
        assert "D***" in anonymized
        assert "John" not in anonymized
        assert "Doe" not in anonymized
    
    def test_generic_anonymization(self, anonymizer):
        """Test generic anonymization for unknown types"""
        text = "sensitive_data"
        anonymized = anonymizer.anonymize_entity(text, "UNKNOWN_TYPE")
        
        assert anonymized != text
        assert len(anonymized) > 0
    
    def test_consistent_masking(self, anonymizer):
        """Test consistent masking produces same output for same input"""
        email = "john@example.com"
        
        mask1 = anonymizer.generate_consistent_mask(email, "EMAIL_ADDRESS")
        mask2 = anonymizer.generate_consistent_mask(email, "EMAIL_ADDRESS")
        
        assert mask1 == mask2
        assert "@example.com" in mask1