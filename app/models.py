"""SQLAlchemy ORM models for the AIML Club database."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    branch = Column(String(100), nullable=True)
    year = Column(String(20), nullable=True)
    roll_number = Column(String(50), nullable=True)
    area_of_interest = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="member")  # member, lead, admin

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event_registrations = relationship("EventRegistration", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  # hackathon, workshop, talk, bootcamp, competition, showcase
    banner_color = Column(String(20), default="blue")  # blue, teal, purple, coral
    emoji = Column(String(10), default="🎯")

    # Scheduling
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)

    # Capacity
    max_spots = Column(Integer, nullable=True)  # None = unlimited
    is_open = Column(Boolean, default=False)  # Registration open/closed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    registrations = relationship("EventRegistration", back_populates="event")

    @property
    def spots_taken(self) -> int:
        return len(self.registrations) if self.registrations else 0

    @property
    def spots_left(self) -> int | None:
        if self.max_spots is None:
            return None
        return max(0, self.max_spots - self.spots_taken)

    def __repr__(self):
        return f"<Event {self.title}>"


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    status = Column(String(20), default="registered")  # registered, waitlisted, cancelled
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="event_registrations")
    event = relationship("Event", back_populates="registrations")

    def __repr__(self):
        return f"<EventRegistration user={self.user_id} event={self.event_id}>"


class SystemSetting(Base):
    __tablename__ = "settings"

    key = Column(String(50), primary_key=True)
    value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
