"""Event routes: list events, register for events."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event, EventRegistration, User
from app.schemas import EventResponse, EventRegistrationResponse, MessageResponse
from app.auth import require_verified_user

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=list[EventResponse])
async def list_events(db: Session = Depends(get_db)):
    """List all events (public, no auth required)."""
    events = db.query(Event).order_by(Event.start_date.desc()).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get a single event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/register", response_model=MessageResponse)
async def register_for_event(
    event_id: str,
    user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
):
    """Register the current user for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if not event.is_open:
        raise HTTPException(status_code=400, detail="Registration for this event is closed")

    # Check if already registered
    existing = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.user_id == user.id,
            EventRegistration.event_id == event_id,
            EventRegistration.status != "cancelled",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You are already registered for this event")

    # Check capacity
    registration_status = "registered"
    if event.max_spots is not None and event.spots_taken >= event.max_spots:
        registration_status = "waitlisted"

    registration = EventRegistration(
        user_id=user.id,
        event_id=event_id,
        status=registration_status,
    )
    db.add(registration)
    db.commit()

    if registration_status == "waitlisted":
        return MessageResponse(
            message="Event is full — you've been added to the waitlist.",
            detail=f"Waitlist position: {event.spots_taken - event.max_spots + 1}",
        )

    return MessageResponse(message=f"Successfully registered for {event.title}!")


@router.get("/my/registrations", response_model=list[EventRegistrationResponse])
async def my_registrations(
    user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
):
    """List the current user's event registrations."""
    return (
        db.query(EventRegistration)
        .filter(EventRegistration.user_id == user.id)
        .order_by(EventRegistration.registered_at.desc())
        .all()
    )
