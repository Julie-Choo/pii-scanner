# tests/test_api/test_endpoints.py
"""
Test API endpoints
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from main import app

class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "PII Scanner API"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "scanner_ready" in data
    
    def test_scan_text_endpoint(self, client):
        """Test text scanning endpoint"""
        request_data = {
            "text": "Contact john.doe@example.com or call (555) 123-4567",
            "confidence_threshold": 0.5
        }
        
        response = client.post("/scan/text", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "summary" in data
        assert "matches" in data
        assert data["summary"]["total_entities"] >= 1
    
    def test_scan_text_empty(self, client):
        """Test scanning empty text"""
        request_data = {"text": "   "}
        
        response = client.post("/scan/text", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_anonymize_text_endpoint(self, client):
        """Test text anonymization endpoint"""
        request_data = {
            "text": "My email is john.doe@company.com and phone is (555) 123-4567"
        }
        
        response = client.post("/anonymize/text", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "anonymized_text" in data
        assert data["anonymized_text"] != data["original_text"]
    
    def test_get_supported_entities(self, client):
        """Test getting supported entities"""
        response = client.get("/scan/supported-entities")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_entities" in data
        assert isinstance(data["supported_entities"], list)
        assert len(data["supported_entities"]) > 0
    
    def test_get_supported_file_types(self, client):
        """Test getting supported file types"""
        response = client.get("/scan/supported-file-types")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_extensions" in data
        assert isinstance(data["supported_extensions"], list)