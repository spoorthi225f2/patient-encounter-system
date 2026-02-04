# Patient Encounter System

A production-ready Python backend system built for managing medical encounters in outpatient clinics. It supports patient registration, doctor management, and appointment scheduling with strict enforcement of healthcare rules and timezone-aware data integrity.

## 🚀 Features

- **Patient Records**: Register and retrieve patients with unique email enforcement.
- **Doctor Profiles**: Manage doctors with active/inactive status and specialization.
- **Smart Scheduling**:
  - Prevents overlapping appointments for the same doctor.
  - Rejects appointments scheduled in the past.
  - Enforces duration limits (15–180 minutes).
- **Timezone-Aware**: All datetime operations use UTC/timezone-aware objects.
- **Production Infrastructure**: CI/CD pipeline with linting, formatting, and security scanning.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: MySQL (hosted on `cp-15.webhostbox.net`)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Dependency Management**: [Poetry](https://python-poetry.org/)
- **CI/CD**: GitHub Actions (Ruff, Black, Bandit, Pytest)

## 📁 Project Structure

```text
patient-encounter-system/
├── src/
│   ├── main.py          # FastAPI app & endpoints
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic & overlap rules
├── tests/               # Pytest suite
├── .github/workflows/   # CI/CD configs
├── .bandit              #BANDIT
├── pyproject.toml       # Poetry dependencies
├── requirements.txt     # Requirements
└── README.md
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Poetry (`pip install poetry`)

### 2. Install Dependencies
```bash
poetry install
```

### 3. Initialize Database
Drops existing tables (prefixed with `spoorthi_`) and recreates schema:
```bash
poetry run python -m src.reset_db
```

### 4. Run Application
```bash
poetry run uvicorn src.main:app --reload
```
- API: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

## 🧪 Testing & Quality

Run tests with coverage:
```bash
# Ensure PYTHONPATH points to root
$env:PYTHONPATH = "."
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## 📡 API Endpoints

### Patients
- `POST /patients`: Register new patient
- `GET /patients/{id}`: Retrieve patient details

### Doctors
- `POST /doctors`: Register new doctor
- `GET /doctors/{id}`: Retrieve doctor details

### Appointments
- `POST /appointments`: Schedule encounter (validates overlaps & duration)
- `GET /appointments?date=YYYY-MM-DD`: List clinic appointments by date
- `GET /appointments?date=YYYY-MM-DD&doctor_id=1`: List doctor-specific appointments

## 🛡️ Business Rules

1. **No Overlaps**: Doctors cannot be double-booked.  
2. **Future-Only**: Appointments must be scheduled ahead of time.  
3. **Duration Control**: Encounters must last between 15–180 minutes.  
4. **Data Integrity**: Records linked to appointments cannot be deleted.
