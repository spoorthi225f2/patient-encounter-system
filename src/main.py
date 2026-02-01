from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from src.database import engine, Base, get_db
from src.models import models
from src.schemas import schemas
from src.services import clinic_service

# Initialize Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Encounter System (MES)")

# --- Patient APIs ---


@app.post("/patients", response_model=schemas.PatientRead, status_code=201)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = (
        db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_p = models.Patient(**patient.model_dump())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p


@app.get("/patients/{patient_id}", response_model=schemas.PatientRead)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


# Added to fix 405 error
@app.get("/patients", response_model=List[schemas.PatientRead])
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()


# --- Doctor APIs ---


@app.post("/doctors", response_model=schemas.DoctorRead, status_code=201)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    db_d = models.Doctor(**doctor.model_dump())
    db.add(db_d)
    db.commit()
    db.refresh(db_d)
    return db_d


@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorRead)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d


@app.get("/doctors", response_model=List[schemas.DoctorRead])
def list_doctors(db: Session = Depends(get_db)):
    return db.query(models.Doctor).all()


# --- Appointment APIs ---


@app.post("/appointments", response_model=schemas.AppointmentRead, status_code=201)
def create_appointment(apt: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return clinic_service.create_appointment(db, apt)


@app.get("/appointments", response_model=List[schemas.AppointmentRead])
def list_appointments(
    date: date = Query(..., alias="date", description="Format: YYYY-MM-DD"),
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieves appointments for a specific date.
    Matches requirement 8: GET /appointments?date=YYYY-MM-DD&doctor_id={optional}
    """
    query = db.query(models.Appointment).filter(
        func.date(models.Appointment.start_time) == date
    )
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
    return query.all()
