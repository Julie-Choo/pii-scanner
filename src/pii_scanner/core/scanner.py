"""
Core PII scanner engine using Microsoft Presidio
"""

import time
import logging
from typing import List, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from .models import PIIMatch, ScanResult, ScanOptions
from .anonymizer import PIIAnonymizer
from ..utils.logger import get_logger
from ..exceptions import ScannerError, InitializationError

logger = get_logger(__name__)

class PIIScanner:
    """Core PII detection and anonymization engine"""
    
    def __init__(self):
        """Initialize the PII scanner with Presidio engines"""
        self._analyzer = None
        self._anonymizer = None
        self._pii_anonymizer = None
        self._initialized = False
        
        try:
            self._initialize()
        except Exception as e:
            logger.error(f"Failed to initialize PII scanner: {e}")
            raise InitializationError(f"Scanner initialization failed: {e}")
    
    def _initialize(self):
        """Initialize Presidio engines"""
        logger.info("Initializing PII scanner engines...")
        
        # Initialize analyzer
        self._analyzer = AnalyzerEngine()
        
        # Initialize anonymizer
        self._anonymizer = AnonymizerEngine()
        
        # Initialize custom anonymizer
        self._pii_anonymizer = PIIAnonymizer()
        
        self._initialized = True
        logger.info("✓ PII scanner initialized successfully")
    
    def is_ready(self) -> bool:
        """Check if scanner is ready for use"""
        return self._initialized and self._analyzer is not None
    
    def scan_text(self, text: str, options: Optional[ScanOptions] = None) -> ScanResult:
        """
        Scan text for PII entities
        
        Args:
            text: Text to scan for PII
            options: Scanning options and configuration
            
        Returns:
            ScanResult containing all detected PII
        """
        if not self.is_ready():
            raise ScannerError("Scanner not initialized")
        
        if not text or not text.strip():
            return ScanResult()
        
        options = options or ScanOptions()
        start_time = time.time()
        
        try:
            # Analyze text with Presidio
            logger.debug(f"Scanning text of length {len(text)} with threshold {options.confidence_threshold}")
            
            analyzer_results = self._analyzer.analyze(
                text=text,
                language=options.language,
                entities=options.entity_types
            )
            
            # Convert results to our format
            matches = []
            for result in analyzer_results:
                if result.score >= options.confidence_threshold:
                    match = self._create_pii_match(
                        text=text,
                        result=result,
                        options=options
                    )
                    matches.append(match)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Scan completed: found {len(matches)} PII entities in {processing_time:.1f}ms")
            
            return ScanResult(
                matches=matches,
                processing_time_ms=processing_time,
                source_info={
                    "type": "text",
                    "length": len(text),
                    "confidence_threshold": options.confidence_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Error during text scanning: {e}")
            raise ScannerError(f"Text scanning failed: {e}")
    
    def _create_pii_match(self, text: str, result, options: ScanOptions) -> PIIMatch:
        """Create PIIMatch from Presidio result"""
        # Extract the actual PII text
        pii_text = text[result.start:result.end]
        
        # Get context if requested
        context = ""
        if options.include_context:
            context = self._get_context(text, result.start, result.end, options.context_window)
        
        # Anonymize if requested
        anonymized_text = ""
        if options.anonymize_results:
            anonymized_text = self._pii_anonymizer.anonymize_entity(pii_text, result.entity_type)
        
        return PIIMatch(
            entity_type=result.entity_type,
            text=pii_text,
            start=result.start,
            end=result.end,
            confidence=result.score,
            context=context,
            anonymized_text=anonymized_text
        )
    
    def _get_context(self, text: str, start: int, end: int, window: int) -> str:
        """Extract context around PII match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        context = text[context_start:context_end]
        # Clean up context - remove extra whitespace
        context = ' '.join(context.split())
        
        # Add ellipsis if truncated
        if context_start > 0 or context_end < len(text):
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."
        
        return context
    
    def anonymize_text(self, text: str, options: Optional[ScanOptions] = None) -> str:
        """
        Anonymize all PII in text
        
        Args:
            text: Text to anonymize
            options: Scanning options
            
        Returns:
            Text with PII anonymized
        """
        if not self.is_ready():
            raise ScannerError("Scanner not initialized")
        
        if not text or not text.strip():
            return text
        
        options = options or ScanOptions()
        
        try:
            # Analyze text first
            analyzer_results = self._analyzer.analyze(
                text=text,
                language=options.language,
                entities=options.entity_types
            )
            
            # Filter by confidence
            filtered_results = [
                result for result in analyzer_results 
                if result.score >= options.confidence_threshold
            ]
            
            # Use Presidio's anonymizer
            anonymized_result = self._anonymizer.anonymize(
                text=text,
                analyzer_results=filtered_results
            )
            
            return anonymized_result.text
            
        except Exception as e:
            logger.error(f"Error during text anonymization: {e}")
            raise ScannerError(f"Text anonymization failed: {e}")
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        try:
            if not self._analyzer:
                return []
            
            # Get supported entities from analyzer
            return self._analyzer.get_supported_entities()
        except Exception as e:
            logger.warning(f"Could not get supported entities: {e}")
            # Return default list
            return [
                "CREDIT_CARD", "CRYPTO", "DATE_TIME", "EMAIL_ADDRESS",
                "IBAN_CODE", "IP_ADDRESS", "LOCATION", "PERSON", 
                "PHONE_NUMBER", "MEDICAL_LICENSE", "URL", "US_BANK_NUMBER",
                "US_DRIVER_LICENSE", "US_ITIN", "US_PASSPORT", "US_SSN"
            ]
    
    def health_check(self) -> dict:
        """Perform health check on scanner"""
        try:
            # Quick test scan
            test_result = self.scan_text("test@example.com")
            
            return {
                "status": "healthy",
                "initialized": self._initialized,
                "analyzer_ready": self._analyzer is not None,
                "anonymizer_ready": self._anonymizer is not None,
                "test_scan_successful": len(test_result.matches) > 0,
                "supported_entities_count": len(self.get_supported_entities())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized
            }

# Global scanner instance for easy access
_scanner_instance = None

def get_scanner() -> PIIScanner:
    """Get global scanner instance (singleton pattern)"""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = PIIScanner()
    return _scanner_instance

def scan_text(text: str, confidence_threshold: float = 0.5, 
              entity_types: Optional[List[str]] = None) -> ScanResult:
    """Convenience function for quick text scanning"""
    options = ScanOptions(
        confidence_threshold=confidence_threshold,
        entity_types=entity_types
    )
    return get_scanner().scan_text(text, options)

def anonymize_text(text: str, confidence_threshold: float = 0.5) -> str:
    """Convenience function for quick text anonymization"""
    options = ScanOptions(confidence_threshold=confidence_threshold)
    return get_scanner().anonymize_text(text, options)