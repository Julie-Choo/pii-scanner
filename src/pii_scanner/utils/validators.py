# src/pii_scanner/utils/validators.py
"""
Input validation utilities
"""

import os
from typing import List, Optional
from ..exceptions import ValidationError

def validate_confidence_threshold(threshold: float) -> float:
    """Validate confidence threshold"""
    if not 0.0 <= threshold <= 1.0:
        raise ValidationError("Confidence threshold must be between 0.0 and 1.0")
    return threshold

def validate_context_window(window: int) -> int:
    """Validate context window size"""
    if window < 0:
        raise ValidationError("Context window must be non-negative")
    if window > 1000:
        raise ValidationError("Context window too large (max 1000)")
    return window

def validate_entity_types(entity_types: Optional[List[str]]) -> Optional[List[str]]:
    """Validate entity types list"""
    if entity_types is None:
        return None
    
    if not isinstance(entity_types, list):
        raise ValidationError("Entity types must be a list")
    
    if not entity_types:
        raise ValidationError("Entity types list cannot be empty")
    
    # Could add validation against supported entity types here
    return entity_types

def validate_file_path(file_path: str) -> str:
    """Validate file path"""
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValidationError(f"Path is not a file: {file_path}")
    
    return file_path

def validate_file_size(file_path: str, max_size_mb: int = 100) -> bool:
    """Validate file size"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise ValidationError(f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)")
        
        return True
    except OSError as e:
        raise ValidationError(f"Could not check file size: {e}")

def validate_text_input(text: str, max_length: int = 1000000) -> str:
    """Validate text input"""
    if not isinstance(text, str):
        raise ValidationError("Text input must be a string")
    
    if len(text) > max_length:
        raise ValidationError(f"Text too long: {len(text)} characters (max: {max_length})")
    
    return text