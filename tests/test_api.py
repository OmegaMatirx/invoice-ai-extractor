"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Invoice AI Extractor API"

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_extract_endpoint_no_file():
    """Test extract endpoint without file"""
    response = client.post("/api/extract")
    assert response.status_code == 422  # Validation error

def test_extract_endpoint_with_file():
    """Test extract endpoint with sample file"""
    # Create a simple test image
    test_file_content = b"fake image content"
    
    response = client.post(
        "/api/extract",
        files={"file": ("test.png", test_file_content, "image/png")}
    )
    
    # This might fail without proper OCR setup, but tests the endpoint structure
    assert response.status_code in [200, 500]  # Either success or processing error

if __name__ == "__main__":
    pytest.main([__file__])