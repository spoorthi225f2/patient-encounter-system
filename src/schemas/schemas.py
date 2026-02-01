from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from pydantic import computed_field
from datetime import timedelta

# from typing import Optional


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorCreate(BaseModel):
    full_name: str
    specialization: str


class DoctorRead(DoctorCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    start_time: datetime
    duration_minutes: int = Field(..., ge=15, le=180)

    @validator("start_time")
    def ensure_timezone_and_future(cls, v):
        if v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if v <= datetime.now(v.tzinfo):
            raise ValueError("Appointment must be in the future")
        return v


# ... keep Patient and Doctor schemas as they were ...


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int

    @computed_field
    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)

    class Config:
        from_attributes = True
