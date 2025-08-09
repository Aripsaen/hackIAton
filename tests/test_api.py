import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_init_bad_request():
    '''Test that the endpoint requires a valid payload.'''
    response = client.post("/upload-init", json={"wrong": "payload"})
    assert response.status_code == 422 # Unprocessable Entity

# A more comprehensive test would mock the GCS client
# and verify the signed URL generation logic.
# For this hackathon, we keep it simple.
def test_upload_init_smoke_test(monkeypatch):
    # Mock the GCS function to avoid real calls
    monkeypatch.setattr("api.gcs.generate_signed_url_for_upload", lambda **kwargs: "http://mock.url/signed")
    
    payload = {
        "case_id": "test-case",
        "filename": "test.pdf",
        "content_type": "application/pdf"
    }
    response = client.post("/upload-init", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "signed_url" in data
    assert "gcs_path" in data
    assert data["gcs_path"] == "raw/test-case/test.pdf"
