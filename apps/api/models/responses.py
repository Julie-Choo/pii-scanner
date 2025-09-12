# apps/api/models/responses.py
"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PIIMatchResponse(BaseModel):
    """Individual PII match in response"""
    entity_type: str = Field(description="Type of PII entity")
    text: str = Field(description="Original text containing PII")
    start: int = Field(description="Start position in text")
    end: int = Field(description="End position in text") 
    confidence: float = Field(description="Detection confidence score")
    confidence_level: str = Field(description="Confidence level category")
    location: str = Field(description="Location where PII was found")
    context: Optional[str] = Field(description="Context around the PII")
    anonymized_text: str = Field(description="Anonymized version")
    timestamp: str = Field(description="Detection timestamp")

class ScanSummary(BaseModel):
    """Summary statistics for scan results"""
    total_entities: int = Field(description="Total PII entities found")
    entity_counts: Dict[str, int] = Field(description="Count by entity type")
    confidence_distribution: Dict[str, int] = Field(description="Count by confidence level")
    average_confidence: float = Field(description="Average confidence score")
    processing_time_ms: float = Field(description="Processing time in milliseconds")

class ScanResponse(BaseModel):
    """Response for scan operations"""
    success: bool = Field(True, description="Operation success status")
    summary: ScanSummary = Field(description="Scan summary")
    matches: List[PIIMatchResponse] = Field(description="Detected PII entities")
    source_info: Dict[str, Any] = Field(description="Information about scanned source")

class AnonymizeResponse(BaseModel):
    """Response for anonymization operations"""
    success: bool = Field(True, description="Operation success status")
    original_text: str = Field(description="Original input text")
    anonymized_text: str = Field(description="Anonymized text")
    entities_anonymized: int = Field(description="Number of entities anonymized")
    processing_time_ms: float = Field(description="Processing time in milliseconds")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Overall health status")
    timestamp: str = Field(description="Health check timestamp")
    scanner_ready: bool = Field(description="Scanner initialization status")
    supported_entities: List[str] = Field(description="Supported PII entity types")
    version: str = Field(description="API version")

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(description="Error type")
    detail: str = Field(description="Detailed error message")
    timestamp: str = Field(description="Error timestamp")