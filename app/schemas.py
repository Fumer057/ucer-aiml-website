"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ── Auth ──

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str


# ── User ──

class UserRegister(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    phone: Optional[str] = None
    branch: str = Field(..., min_length=1)
    year: str = Field(..., min_length=1)
    roll_number: str = Field(..., min_length=1)
    area_of_interest: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    roll_number: Optional[str] = None
    area_of_interest: Optional[str] = None
    is_verified: bool
    is_admin: bool
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None


# ── Events ──

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: str = Field(..., pattern="^(hackathon|workshop|talk|bootcamp|competition|showcase)$")
    banner_color: str = "blue"
    emoji: str = "🎯"
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    max_spots: Optional[int] = None
    is_open: bool = False


class EventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    event_type: str
    banner_color: str
    emoji: str
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    max_spots: Optional[int] = None
    spots_taken: int = 0
    spots_left: Optional[int] = None
    is_open: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    banner_color: Optional[str] = None
    emoji: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    max_spots: Optional[int] = None
    is_open: Optional[bool] = None


# ── Event Registration ──

class EventRegistrationResponse(BaseModel):
    id: str
    event_id: str
    user_id: str
    status: str
    registered_at: datetime

    model_config = {"from_attributes": True}


class AdminEventRegistrationResponse(BaseModel):
    id: str
    event_id: str
    user: UserResponse
    status: str
    registered_at: datetime

    model_config = {"from_attributes": True}


# ── Generic ──

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


# ── Settings ──

class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime

    model_config = {"from_attributes": True}
