import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from src.main import app
from src.database import engine, Base

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Ensure tables are created before tests run
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: Base.metadata.drop_all(bind=engine) # Uncomment to wipe after tests


def test_create_patient_success():
    payload = {
        "first_name": "Spoorthi",
        "last_name": "--",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "phone_number": "9876543210",
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]


def test_create_patient_duplicate_email():
    email = "duplicate@example.com"
    payload = {"first_name": "A", "last_name": "B", "email": email, "phone_number": "1"}
    client.post("/patients", json=payload)
    # Try again
    response = client.post("/patients", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_get_patient_not_found():
    response = client.get("/patients/9999")
    assert response.status_code == 404


def test_create_appointment_logic():
    # 1. Create Patient & Doctor
    p_resp = client.post(
        "/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john_{datetime.now().timestamp()}@example.com",
            "phone_number": "000",
        },
    )
    d_resp = client.post(
        "/doctors", json={"full_name": "Dr. House", "specialization": "Diagnostics"}
    )

    p_id = p_resp.json()["id"]
    d_id = d_resp.json()["id"]

    # Future time (Tomorrow at 10 AM)
    start_time = (
        (datetime.now(timezone.utc) + timedelta(days=1))
        .replace(hour=10, minute=0)
        .isoformat()
    )

    # 2. Valid Appointment
    apt_payload = {
        "patient_id": p_id,
        "doctor_id": d_id,
        "start_time": start_time,
        "duration_minutes": 30,
    }
    response = client.post("/appointments", json=apt_payload)
    assert response.status_code == 201

    # 3. Conflict (Overlap)
    response_overlap = client.post("/appointments", json=apt_payload)
    assert response_overlap.status_code == 409


def test_appointment_past_date_fails():
    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "start_time": past_time,
        "duration_minutes": 30,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_appointment_duration_invalid():
    # Too short
    payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "duration_minutes": 5,
    }
    assert client.post("/appointments", json=payload).status_code == 422
