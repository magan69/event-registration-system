from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from .models import RegistrationStatus


# ---------- Users ----------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Events ----------
class EventCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    location: Optional[str] = None
    date: datetime
    capacity: int = Field(..., gt=0)


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0)


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    date: datetime
    capacity: int
    confirmed_count: int
    waitlisted_count: int
    spots_left: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Registrations ----------
class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int


class RegistrationOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: RegistrationStatus
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
