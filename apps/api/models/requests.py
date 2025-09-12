# apps/api/models/requests.py
"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TextScanRequest(BaseModel):
    """Request model for text scanning"""
    text: str = Field(..., min_length=1, max_length=1000000, description="Text to scan for PII")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    entity_types: Optional[List[str]] = Field(None, description="Specific entity types to detect")
    include_context: Optional[bool] = Field(True, description="Include context around detected PII")
    context_window: Optional[int] = Field(50, ge=10, le=200, description="Size of context window")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v

class AnonymizeRequest(BaseModel):
    """Request model for text anonymization"""
    text: str = Field(..., min_length=1, description="Text to anonymize")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    entity_types: Optional[List[str]] = Field(None, description="Entity types to anonymize")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v

class FileScanConfig(BaseModel):
    """Configuration for file scanning"""
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    entity_types: Optional[List[str]] = Field(None)
    include_context: Optional[bool] = Field(True)
    context_window: Optional[int] = Field(50, ge=10, le=200)
    max_file_size_mb: Optional[int] = Field(10, ge=1, le=100)