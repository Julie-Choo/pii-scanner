"""
Data models and types for PII scanner
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class EntityType(Enum):
    """Supported PII entity types"""
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    US_SSN = "US_SSN"
    CREDIT_CARD = "CREDIT_CARD"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    IP_ADDRESS = "IP_ADDRESS"
    DATE_TIME = "DATE_TIME"
    US_DRIVER_LICENSE = "US_DRIVER_LICENSE"
    US_PASSPORT = "US_PASSPORT"
    CRYPTO = "CRYPTO"
    IBAN_CODE = "IBAN_CODE"
    URL = "URL"
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    US_BANK_NUMBER = "US_BANK_NUMBER"
    US_ITIN = "US_ITIN"
    NRP = "NRP"

class ConfidenceLevel(Enum):
    """Confidence level categories"""
    LOW = "low"        # 0.0 - 0.6
    MEDIUM = "medium"  # 0.6 - 0.8
    HIGH = "high"      # 0.8 - 1.0

@dataclass
class PIIMatch:
    """Represents a single PII detection result"""
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    location: str = ""
    context: str = ""
    anonymized_text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get confidence level category"""
        if self.confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "entity_type": self.entity_type,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "location": self.location,
            "context": self.context,
            "anonymized_text": self.anonymized_text,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ScanResult:
    """Complete scan result with metadata"""
    matches: List[PIIMatch] = field(default_factory=list)
    total_entities: int = 0
    processing_time_ms: float = 0.0
    source_info: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Update total_entities after initialization"""
        self.total_entities = len(self.matches)
    
    @property
    def entity_counts(self) -> Dict[str, int]:
        """Count entities by type"""
        counts = {}
        for match in self.matches:
            counts[match.entity_type] = counts.get(match.entity_type, 0) + 1
        return counts
    
    @property
    def confidence_distribution(self) -> Dict[str, int]:
        """Count entities by confidence level"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        for match in self.matches:
            distribution[match.confidence_level.value] += 1
        return distribution
    
    @property
    def average_confidence(self) -> float:
        """Calculate average confidence score"""
        if not self.matches:
            return 0.0
        return sum(match.confidence for match in self.matches) / len(self.matches)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get scan summary"""
        return {
            "total_entities": self.total_entities,
            "entity_counts": self.entity_counts,
            "confidence_distribution": self.confidence_distribution,
            "average_confidence": self.average_confidence,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "matches": [match.to_dict() for match in self.matches],
            "summary": self.get_summary(),
            "source_info": self.source_info
        }

@dataclass
class ScanOptions:
    """Configuration options for scanning"""
    confidence_threshold: float = 0.5
    entity_types: Optional[List[str]] = None
    include_context: bool = True
    context_window: int = 50
    anonymize_results: bool = True
    language: str = "en"
    
    def __post_init__(self):
        """Validate options after initialization"""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        
        if self.context_window < 0:
            raise ValueError("context_window must be non-negative")
        
        if self.entity_types is None:
            # Default entity types to scan for
            self.entity_types = [
                EntityType.EMAIL_ADDRESS.value,
                EntityType.PHONE_NUMBER.value,
                EntityType.US_SSN.value,
                EntityType.CREDIT_CARD.value,
                EntityType.PERSON.value
            ]

@dataclass
class FileInfo:
    """Information about a file being scanned"""
    path: str
    name: str
    extension: str
    size_bytes: int
    encoding: str = "utf-8"
    
    @classmethod
    def from_path(cls, file_path: str) -> 'FileInfo':
        """Create FileInfo from file path"""
        import os
        
        name = os.path.basename(file_path)
        extension = os.path.splitext(name)[1].lower()
        size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return cls(
            path=file_path,
            name=name,
            extension=extension,
            size_bytes=size_bytes
        )

class ScanStatus(Enum):
    """Status of a scan operation"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"