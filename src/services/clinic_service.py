from datetime import timedelta, timezone

# from sqlalchemy import or_
from src.models import models


def check_overlap(db, doctor_id, start_time, duration_minutes):
    """
    Check if a doctor has any overlapping appointments.
    Calculation: (ExistingStart < NewEnd) AND (ExistingEnd > NewStart)
    """
    # 1. Force the incoming start_time to be naive (UTC) for comparison
    if start_time.tzinfo is not None:
        start_time = start_time.astimezone(timezone.utc).replace(tzinfo=None)

    # 2. Calculate the end time of the new appointment
    new_end_time = start_time + timedelta(minutes=duration_minutes)

    # 3. Fetch potential overlaps for this doctor
    # We filter by doctor and check if existing starts before our new end
    overlap = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.start_time < new_end_time,
        )
        .all()
    )

    # 4. Refine overlap logic in Python to be database-agnostic
    for apt in overlap:
        # Ensure the database timestamp is also naive for comparison
        apt_start = apt.start_time
        if apt_start.tzinfo is not None:
            apt_start = apt_start.astimezone(timezone.utc).replace(tzinfo=None)

        apt_end = apt_start + timedelta(minutes=apt.duration_minutes)

        # Overlap exists if existing end is after our new start
        if apt_end > start_time:
            return True

    return False


def create_appointment(db, obj_in):
    """
    Main entry point used by main.py to schedule an appointment.
    """
    # Check for conflicts
    if check_overlap(db, obj_in.doctor_id, obj_in.start_time, obj_in.duration_minutes):
        from fastapi import HTTPException

        raise HTTPException(status_code=409, detail="Doctor has a scheduling conflict")

    # Create the record
    db_obj = models.Appointment(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
