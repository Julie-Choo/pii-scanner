"""
PII anonymization utilities
"""

import re
import hashlib
from typing import Dict, Callable
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PIIAnonymizer:
    """Handles anonymization of different PII types"""
    
    def __init__(self):
        """Initialize anonymizer with entity-specific handlers"""
        self.anonymizers: Dict[str, Callable[[str], str]] = {
            "EMAIL_ADDRESS": self._anonymize_email,
            "PHONE_NUMBER": self._anonymize_phone,
            "US_SSN": self._anonymize_ssn,
            "CREDIT_CARD": self._anonymize_credit_card,
            "PERSON": self._anonymize_person,
            "LOCATION": self._anonymize_location,
            "IP_ADDRESS": self._anonymize_ip,
            "US_DRIVER_LICENSE": self._anonymize_driver_license,
            "US_PASSPORT": self._anonymize_passport,
            "DATE_TIME": self._anonymize_datetime,
            "URL": self._anonymize_url,
            "CRYPTO": self._anonymize_crypto,
            "IBAN_CODE": self._anonymize_iban,
            "MEDICAL_LICENSE": self._anonymize_medical_license,
            "US_BANK_NUMBER": self._anonymize_bank_number,
            "US_ITIN": self._anonymize_itin,
            "NRP": self._anonymize_nrp
        }
    
    def anonymize_entity(self, text: str, entity_type: str) -> str:
        """
        Anonymize a single PII entity
        
        Args:
            text: The PII text to anonymize
            entity_type: Type of PII entity
            
        Returns:
            Anonymized version of the text
        """
        if not text:
            return text
        
        # Get specific anonymizer for entity type
        anonymizer = self.anonymizers.get(entity_type, self._anonymize_generic)
        
        try:
            return anonymizer(text)
        except Exception as e:
            logger.warning(f"Error anonymizing {entity_type}: {e}")
            return self._anonymize_generic(text)
    
    def _anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if "@" not in email:
            return self._mask_text(email)
        
        local, domain = email.split("@", 1)
        
        # Keep first 2 characters of local part
        if len(local) <= 2:
            anonymized_local = "*" * len(local)
        else:
            anonymized_local = local[:2] + "*" * (len(local) - 2)
        
        return f"{anonymized_local}@{domain}"
    
    def _anonymize_phone(self, phone: str) -> str:
        """Anonymize phone number"""
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) >= 4:
            # Keep last 4 digits
            return f"***-***-{digits[-4:]}"
        else:
            return "***-***-****"
    
    def _anonymize_ssn(self, ssn: str) -> str:
        """Anonymize Social Security Number"""
        # Extract digits only
        digits = re.sub(r'\D', '', ssn)
        
        if len(digits) >= 4:
            # Keep last 4 digits
            return f"***-**-{digits[-4:]}"
        else:
            return "***-**-****"
    
    def _anonymize_credit_card(self, cc: str) -> str:
        """Anonymize credit card number"""
        # Extract digits only
        digits = re.sub(r'\D', '', cc)
        
        if len(digits) >= 4:
            # Keep last 4 digits
            return f"****-****-****-{digits[-4:]}"
        else:
            return "****-****-****-****"
    
    def _anonymize_person(self, name: str) -> str:
        """Anonymize person name"""
        # Split name into parts
        parts = name.strip().split()
        
        if not parts:
            return "[NAME]"
        elif len(parts) == 1:
            # Single name - keep first letter
            return f"{parts[0][0]}***" if parts[0] else "[NAME]"
        else:
            # Multiple parts - keep first letter of each
            anonymized_parts = []
            for part in parts:
                if part:
                    anonymized_parts.append(f"{part[0]}***")
                else:
                    anonymized_parts.append("***")
            return " ".join(anonymized_parts)
    
    def _anonymize_location(self, location: str) -> str:
        """Anonymize location"""
        # Simple masking for locations
        if len(location) <= 4:
            return "[LOCATION]"
        else:
            return f"{location[:2]}***{location[-1:]}"
    
    def _anonymize_ip(self, ip: str) -> str:
        """Anonymize IP address"""
        # Keep first octet, mask the rest
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.***.***.***"
        else:
            return "***.***.***.***"
    
    def _anonymize_driver_license(self, dl: str) -> str:
        """Anonymize driver license"""
        if len(dl) >= 4:
            return f"***{dl[-4:]}"
        else:
            return "[LICENSE]"
    
    def _anonymize_passport(self, passport: str) -> str:
        """Anonymize passport number"""
        if len(passport) >= 3:
            return f"**{passport[-3:]}"
        else:
            return "[PASSPORT]"
    
    def _anonymize_datetime(self, datetime_str: str) -> str:
        """Anonymize date/time"""
        # Simple date anonymization - could be more sophisticated
        return "[DATE]"
    
    def _anonymize_url(self, url: str) -> str:
        """Anonymize URL"""
        # Keep protocol and domain structure
        if "://" in url:
            protocol, rest = url.split("://", 1)
            if "/" in rest:
                domain, path = rest.split("/", 1)
                return f"{protocol}://{self._mask_domain(domain)}/***"
            else:
                return f"{protocol}://{self._mask_domain(rest)}"
        else:
            return "[URL]"
    
    def _anonymize_crypto(self, crypto: str) -> str:
        """Anonymize cryptocurrency address"""
        if len(crypto) >= 8:
            return f"{crypto[:4]}***{crypto[-4:]}"
        else:
            return "[CRYPTO]"
    
    def _anonymize_iban(self, iban: str) -> str:
        """Anonymize IBAN code"""
        if len(iban) >= 6:
            return f"{iban[:2]}**{iban[-4:]}"
        else:
            return "[IBAN]"
    
    def _anonymize_medical_license(self, license_num: str) -> str:
        """Anonymize medical license"""
        return "[MED_LICENSE]"
    
    def _anonymize_bank_number(self, bank_num: str) -> str:
        """Anonymize bank account number"""
        if len(bank_num) >= 4:
            return f"***{bank_num[-4:]}"
        else:
            return "[ACCOUNT]"
    
    def _anonymize_itin(self, itin: str) -> str:
        """Anonymize Individual Taxpayer Identification Number"""
        digits = re.sub(r'\D', '', itin)
        if len(digits) >= 4:
            return f"9**-**-{digits[-4:]}"
        else:
            return "9**-**-****"
    
    def _anonymize_nrp(self, nrp: str) -> str:
        """Anonymize National Registry Person number"""
        return "[NRP]"
    
    def _mask_domain(self, domain: str) -> str:
        """Mask domain name while preserving structure"""
        parts = domain.split(".")
        if len(parts) >= 2:
            # Keep TLD, mask the rest
            masked_parts = ["***" for _ in parts[:-1]] + [parts[-1]]
            return ".".join(masked_parts)
        else:
            return "***"
    
    def _mask_text(self, text: str, show_chars: int = 2) -> str:
        """Generic text masking"""
        if len(text) <= show_chars:
            return "*" * len(text)
        else:
            return f"{text[:show_chars]}{'*' * (len(text) - show_chars * 2)}{text[-show_chars:]}"
    
    def _anonymize_generic(self, text: str) -> str:
        """Generic anonymization for unknown entity types"""
        return self._mask_text(text)
    
    def generate_consistent_mask(self, text: str, entity_type: str) -> str:
        """
        Generate consistent anonymization that's the same for identical inputs
        Useful for maintaining referential integrity in datasets
        """
        # Create hash-based consistent mask
        hash_input = f"{entity_type}:{text}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Format based on entity type
        if entity_type == "EMAIL_ADDRESS":
            return f"user_{hash_value}@example.com"
        elif entity_type == "PHONE_NUMBER":
            return f"555-{hash_value[:3]}-{hash_value[3:7]}"
        elif entity_type == "US_SSN":
            return f"***-**-{hash_value[:4]}"
        elif entity_type == "PERSON":
            return f"Person_{hash_value[:4]}"
        else:
            return f"[{entity_type}_{hash_value[:6]}]"