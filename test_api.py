import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.dependencies import init_pipelines, get_clinical_pipeline, get_index_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_dependencies():
    # Ensure dependencies are initialized before running tests
    init_pipelines()

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_note_empty():
    response = client.post("/process_note", json={"clinical_note": "   "})
    assert response.status_code == 400
    assert "Clinical note cannot be empty" in response.json()["detail"]

def test_process_note_success():
    note = "Patient is taking Actemra for arthritis."
    response = client.post("/process_note", json={"clinical_note": note})
    assert response.status_code == 200
    data = response.json()
    assert "structured_output" in data
    assert "safety_decisions" in data
    assert "aggregated_evidence" in data
    assert "raw_ranking_results" in data

    # Check that output generator output structure exists
    assert "suspected_drug" in data["structured_output"]

def test_rebuild_indexes():
    # Note: This might take a little while as it actually runs the chunker and indexing
    response = client.post("/rebuild_indexes")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Indexes rebuilt successfully."
