# apps/api/routes/scanner.py
"""
Scanning endpoints
"""

import tempfile
import os
import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from pii_scanner import get_scanner, ScanOptions, FileInfo
from pii_scanner.file_handlers import FileHandlerFactory
from ..models.requests import TextScanRequest, FileScanConfig
from ..models.responses import ScanResponse, PIIMatchResponse, ScanSummary

router = APIRouter()

# Initialize scanner and file factory
scanner = get_scanner()
file_factory = FileHandlerFactory(scanner)

def _pii_match_to_response(match) -> PIIMatchResponse:
    """Convert PIIMatch to response model"""
    return PIIMatchResponse(
        entity_type=match.entity_type,
        text=match.text,
        start=match.start,
        end=match.end,
        confidence=match.confidence,
        confidence_level=match.confidence_level.value,
        location=match.location,
        context=match.context or "",
        anonymized_text=match.anonymized_text,
        timestamp=match.timestamp.isoformat()
    )

def _create_scan_response(result) -> ScanResponse:
    """Create scan response from scan result"""
    summary_data = result.get_summary()
    
    summary = ScanSummary(
        total_entities=result.total_entities,
        entity_counts=result.entity_counts,
        confidence_distribution=result.confidence_distribution,
        average_confidence=result.average_confidence,
        processing_time_ms=result.processing_time_ms
    )
    
    matches = [_pii_match_to_response(match) for match in result.matches]
    
    return ScanResponse(
        success=True,
        summary=summary,
        matches=matches,
        source_info=result.source_info
    )

@router.post("/text", response_model=ScanResponse)
async def scan_text(request: TextScanRequest):
    """Scan text for PII entities"""
    
    if not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    try:
        # Configure scan options
        options = ScanOptions(
            confidence_threshold=request.confidence_threshold,
            entity_types=request.entity_types,
            include_context=request.include_context,
            context_window=request.context_window
        )
        
        # Perform scan
        result = scanner.scan_text(request.text, options)
        
        # Return formatted response
        return _create_scan_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scanning failed: {str(e)}")

@router.post("/file", response_model=ScanResponse)
async def scan_file(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,
    include_context: bool = True
):
    """Scan uploaded file for PII"""
    
    if not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if file.size and file.size > max_size:
        raise HTTPException(status_code=413, detail=f"File too large (max {max_size//1024//1024}MB)")
    
    # Check file type
    supported_extensions = file_factory.get_supported_extensions()
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {supported_extensions}"
        )
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Create file info
        file_info = FileInfo.from_path(tmp_path)
        file_info.name = file.filename or "uploaded_file"
        
        # Configure scan options
        options = ScanOptions(
            confidence_threshold=confidence_threshold,
            include_context=include_context
        )
        
        # Get handler and scan
        handler = file_factory.get_handler(file_info)
        result = handler.scan_file(file_info, options)
        
        # Return formatted response
        return _create_scan_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File scanning failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass

@router.get("/supported-entities")
async def get_supported_entities():
    """Get list of supported PII entity types"""
    
    if not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    try:
        entities = scanner.get_supported_entities()
        return {
            "supported_entities": entities,
            "total_count": len(entities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")

@router.get("/supported-file-types")
async def get_supported_file_types():
    """Get list of supported file types"""
    
    extensions = file_factory.get_supported_extensions()
    return {
        "supported_extensions": extensions,
        "total_count": len(extensions)
    }