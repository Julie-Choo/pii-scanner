# apps/api/main.py
"""
Main FastAPI application for PII scanning
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scanner import router as scanner_router
from routes.anonymizer import router as anonymizer_router  
from routes.health import router as health_router
from middleware.cors import setup_cors
from pii_scanner import get_config

# Get configuration
config = get_config()

# Initialize FastAPI app
app = FastAPI(
    title="PII Scanner API",
    description="Advanced PII detection and anonymization using Microsoft Presidio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_cors(app)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(scanner_router, prefix="/scan", tags=["scanning"])
app.include_router(anonymizer_router, prefix="/anonymize", tags=["anonymization"])

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "PII Scanner API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    api_config = config.get_section("api")
    
    print("🚀 Starting PII Scanner API...")
    print(f"📖 Documentation: http://{api_config['host']}:{api_config['port']}/docs")
    
    uvicorn.run(
        "main:app",
        host=api_config["host"],
        port=api_config["port"],
        reload=True
    )