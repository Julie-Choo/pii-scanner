# apps/api/routes/anonymizer.py
"""
Anonymization endpoints
"""

from fastapi import APIRouter, HTTPException
from pii_scanner import get_scanner, ScanOptions
from ..models.requests import AnonymizeRequest
from ..models.responses import AnonymizeResponse

router = APIRouter()

# Initialize scanner
scanner = get_scanner()

@router.post("/text", response_model=AnonymizeResponse)
async def anonymize_text(request: AnonymizeRequest):
    """Anonymize PII in text"""
    
    if not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    try:
        import time
        start_time = time.time()
        
        # Configure options
        options = ScanOptions(
            confidence_threshold=request.confidence_threshold,
            entity_types=request.entity_types
        )
        
        # First scan to count entities
        scan_result = scanner.scan_text(request.text, options)
        entities_count = len(scan_result.matches)
        
        # Anonymize text
        anonymized_text = scanner.anonymize_text(request.text, options)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnonymizeResponse(
            success=True,
            original_text=request.text,
            anonymized_text=anonymized_text,
            entities_anonymized=entities_count,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")