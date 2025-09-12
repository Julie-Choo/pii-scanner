#!/usr/bin/env python3
"""
Fixed version of run_api.py - Copy this over your existing run_api.py
"""

import sys
from pathlib import Path

# Add src to path for pii_scanner
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# All imports in one place
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import tempfile
import os
from datetime import datetime

# Import PII Scanner and file handlers
print("🔄 Loading PII Scanner...")
try:
    from pii_scanner import get_scanner, ScanOptions, scan_text
    from pii_scanner.file_handlers import FileHandlerFactory
    from pii_scanner.core.models import FileInfo
    scanner = get_scanner()
    file_factory = FileHandlerFactory(scanner)
    print(f"✅ PII Scanner loaded - {len(scanner.get_supported_entities())} entity types supported")
    print(f"📁 File handlers loaded - {len(file_factory.get_supported_extensions())} file types supported")
except Exception as e:
    print(f"❌ Failed to load PII Scanner: {e}")
    scanner = None
    file_factory = None

# Create FastAPI app
app = FastAPI(
    title="PII Scanner API",
    description="PII detection and anonymization API with file upload",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class TextScanRequest(BaseModel):
    text: str
    confidence_threshold: Optional[float] = 0.5
    entity_types: Optional[List[str]] = None

class AnonymizeRequest(BaseModel):
    text: str
    confidence_threshold: Optional[float] = 0.5

# Response models
class PIIEntity(BaseModel):
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    anonymized_text: str

class ScanResponse(BaseModel):
    success: bool
    total_entities: int
    entities: List[PIIEntity]
    processing_time_ms: float
    source_info: Optional[dict] = None

class FileScanResponse(BaseModel):
    success: bool
    file_name: str
    file_size: int
    file_type: str
    total_entities: int
    entities: List[PIIEntity]
    processing_time_ms: float
    source_info: dict

class AnonymizeResponse(BaseModel):
    success: bool
    original_text: str
    anonymized_text: str
    entities_found: int
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    scanner_ready: bool
    timestamp: str
    supported_entities: List[str]

# API Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "PII Scanner API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "scan_text": "/scan/text",
            "scan_file": "/scan/file",
            "anonymize": "/anonymize/text",
            "health": "/health",
            "entities": "/scan/supported-entities",
            "file_types": "/scan/supported-file-types"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if scanner and scanner.is_ready():
        try:
            supported = scanner.get_supported_entities()
            status = "healthy"
            ready = True
        except:
            supported = []
            status = "degraded"
            ready = False
    else:
        supported = []
        status = "unhealthy"
        ready = False
    
    return HealthResponse(
        status=status,
        scanner_ready=ready,
        timestamp=datetime.now().isoformat(),
        supported_entities=supported
    )

@app.post("/scan/text", response_model=ScanResponse)
async def scan_text_endpoint(request: TextScanRequest):
    """Scan text for PII entities"""
    if not scanner or not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        start_time = time.time()
        
        # Create options
        options = ScanOptions(
            confidence_threshold=request.confidence_threshold,
            entity_types=request.entity_types
        )
        
        # Scan text
        result = scanner.scan_text(request.text, options)
        
        # Convert to response format
        entities = []
        for match in result.matches:
            entities.append(PIIEntity(
                entity_type=match.entity_type,
                text=match.text,
                start=match.start,
                end=match.end,
                confidence=match.confidence,
                anonymized_text=match.anonymized_text
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        return ScanResponse(
            success=True,
            total_entities=len(entities),
            entities=entities,
            processing_time_ms=processing_time,
            source_info={
                "type": "text",
                "length": len(request.text),
                "confidence_threshold": request.confidence_threshold
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scanning failed: {str(e)}")

@app.post("/scan/file", response_model=FileScanResponse)
async def scan_file_endpoint(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,
    entity_types: Optional[str] = None,
    include_context: bool = True
):
    """Scan uploaded file for PII entities"""
    if not scanner or not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    if not file_factory:
        raise HTTPException(status_code=503, detail="File handlers not available")
    
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
        start_time = time.time()
        
        # Create file info
        file_info = FileInfo.from_path(tmp_path)
        file_info.name = file.filename or "uploaded_file"
        
        # Parse entity types if provided
        entity_types_list = None
        if entity_types:
            entity_types_list = [et.strip() for et in entity_types.split(",")]
        
        # Configure scan options
        options = ScanOptions(
            confidence_threshold=confidence_threshold,
            entity_types=entity_types_list,
            include_context=include_context
        )
        
        # Get handler and scan
        handler = file_factory.get_handler(file_info)
        result = handler.scan_file(file_info, options)
        
        # Convert to response format
        entities = []
        for match in result.matches:
            entities.append(PIIEntity(
                entity_type=match.entity_type,
                text=match.text,
                start=match.start,
                end=match.end,
                confidence=match.confidence,
                anonymized_text=match.anonymized_text
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        return FileScanResponse(
            success=True,
            file_name=file.filename or "uploaded_file",
            file_size=file.size or 0,
            file_type=file_ext,
            total_entities=len(entities),
            entities=entities,
            processing_time_ms=processing_time,
            source_info=result.source_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File scanning failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass

@app.post("/anonymize/text", response_model=AnonymizeResponse)
async def anonymize_text_endpoint(request: AnonymizeRequest):
    """Anonymize PII in text"""
    if not scanner or not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        start_time = time.time()
        
        # First scan to count entities
        options = ScanOptions(confidence_threshold=request.confidence_threshold)
        scan_result = scanner.scan_text(request.text, options)
        
        # Then anonymize
        anonymized = scanner.anonymize_text(request.text, options)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnonymizeResponse(
            success=True,
            original_text=request.text,
            anonymized_text=anonymized,
            entities_found=len(scan_result.matches),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

@app.get("/scan/supported-entities")
async def get_supported_entities():
    """Get list of supported PII entity types"""
    if not scanner or not scanner.is_ready():
        raise HTTPException(status_code=503, detail="Scanner not ready")
    
    try:
        entities = scanner.get_supported_entities()
        return {
            "supported_entities": entities,
            "total_count": len(entities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")

@app.get("/scan/supported-file-types")
async def get_supported_file_types():
    """Get list of supported file types for upload"""
    if not file_factory:
        raise HTTPException(status_code=503, detail="File handlers not available")
    
    try:
        extensions = file_factory.get_supported_extensions()
        
        return {
            "supported_extensions": extensions,
            "total_count": len(extensions),
            "max_file_size_mb": 10,
            "upload_endpoint": "/scan/file"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file types: {str(e)}")

@app.get("/test")
async def quick_test():
    """Quick test endpoint to verify everything works"""
    if not scanner or not scanner.is_ready():
        return {"status": "error", "message": "Scanner not ready"}
    
    try:
        # Test scan
        test_text = "Contact John Doe at john.doe@company.com or call (555) 123-4567"
        result = scan_text(test_text)
        
        # Test file handlers
        file_types = []
        if file_factory:
            file_types = file_factory.get_supported_extensions()
        
        return {
            "status": "success",
            "message": "PII Scanner is working correctly",
            "test_result": {
                "text": test_text,
                "entities_found": result.total_entities,
                "entity_types": list(result.entity_counts.keys()) if result.entity_counts else []
            },
            "capabilities": {
                "text_scanning": True,
                "file_scanning": file_factory is not None,
                "supported_file_types": file_types,
                "anonymization": True
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Test failed: {str(e)}"}

def main():
    """Run the API server"""
    print("\n🚀 PII Scanner API")
    print("=" * 40)
    
    if not scanner:
        print("❌ PII Scanner failed to initialize")
        print("💡 Make sure you have installed:")
        print("   pip install presidio-analyzer presidio-anonymizer spacy")
        print("   python -m spacy download en_core_web_sm")
        return
    
    print("✅ PII Scanner ready")
    print(f"📊 {len(scanner.get_supported_entities())} entity types supported")
    if file_factory:
        print(f"📁 {len(file_factory.get_supported_extensions())} file types supported for upload")
    print("\n🌐 Starting API server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🧪 Quick Test: http://localhost:8000/test")
    print("📁 File Types: http://localhost:8000/scan/supported-file-types")
    print("⏹️ Press Ctrl+C to stop")
    
    try:
        import uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload to avoid import issues
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()