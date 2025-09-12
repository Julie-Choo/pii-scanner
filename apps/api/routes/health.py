# apps/api/routes/health.py
"""
Health check endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pii_scanner import get_scanner
from ..models.responses import HealthResponse

router = APIRouter()

# Initialize scanner
scanner = get_scanner()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    
    try:
        # Get scanner health
        scanner_health = scanner.health_check() if scanner else {"status": "unhealthy"}
        
        # Get supported entities
        supported_entities = []
        if scanner and scanner.is_ready():
            try:
                supported_entities = scanner.get_supported_entities()
            except:
                pass
        
        return HealthResponse(
            status=scanner_health.get("status", "unhealthy"),
            timestamp=datetime.now().isoformat(),
            scanner_ready=scanner_health.get("initialized", False),
            supported_entities=supported_entities,
            version="1.0.0"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/ready")
async def readiness_check():
    """Simple readiness check"""
    
    if scanner and scanner.is_ready():
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Simple liveness check"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}