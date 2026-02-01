from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.models import Doctor, Appointment
from datetime import timedelta
from sqlalchemy import func


def check_overlap(db: Session, doctor_id: int, start_time, duration: int):
    end_time = start_time + timedelta(minutes=duration)

    # Overlap logic: (ExistingStart < NewEnd) AND (ExistingEnd > NewStart)
    overlap = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time < end_time,
            func.adddate(
                Appointment.start_time,
                func.interval(Appointment.duration_minutes, "MINUTE"),
            )
            > start_time,
        )
        .first()
    )

    return overlap is not None


def create_appointment(db: Session, obj_in):
    doctor = db.query(Doctor).filter(Doctor.id == obj_in.doctor_id).first()
    if not doctor or not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor not found or inactive")

    if check_overlap(db, obj_in.doctor_id, obj_in.start_time, obj_in.duration_minutes):
        raise HTTPException(status_code=409, detail="Appointment overlap detected")

    db_obj = Appointment(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
