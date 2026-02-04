import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from src.main import app
from src.database import Base, get_db

# 1. Setup SQLite Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.sqlite"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Dependency Override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Create tables in SQLite
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)


def test_create_patient_success():
    payload = {
        "first_name": "Spoorthi",
        "last_name": "--",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "phone_number": "9879797979",
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]


def test_create_patient_duplicate_email():
    email = "duplicate@example.com"
    payload = {"first_name": "A", "last_name": "B", "email": email, "phone_number": "1"}
    client.post("/patients", json=payload)
    response = client.post("/patients", json=payload)
    assert response.status_code == 400


def test_appointment_logic():
    # 1. Setup Patient and Doctor
    p_resp = client.post(
        "/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "phone_number": "123",
        },
    )
    d_resp = client.post(
        "/doctors", json={"full_name": "Dr. House", "specialization": "Diagnostics"}
    )

    p_id = p_resp.json()["id"]
    d_id = d_resp.json()["id"]

    # 2. Valid Appointment (Future)
    start_time = (
        (datetime.now(timezone.utc) + timedelta(days=1))
        .replace(hour=10, minute=0)
        .isoformat()
    )
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
