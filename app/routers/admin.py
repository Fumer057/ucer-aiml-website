"""Admin routes: manage members, events, and view analytics."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Event, EventRegistration
from app.schemas import EventCreate, EventUpdate, EventResponse, MessageResponse, UserResponse
from app.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Members ──

@router.get("/members", response_model=list[UserResponse])
async def list_members(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all registered members."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/members/{user_id}", response_model=UserResponse)
async def get_member(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get a single member by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/members/{user_id}/toggle-admin", response_model=MessageResponse)
async def toggle_admin(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Toggle admin status of a member."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin status")
    user.is_admin = not user.is_admin
    db.commit()
    status = "granted" if user.is_admin else "revoked"
    return MessageResponse(message=f"Admin access {status} for {user.first_name} {user.last_name}")


@router.patch("/members/{user_id}/toggle-verify", response_model=MessageResponse)
async def toggle_verify(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Manually toggle verification status of a member."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = not user.is_verified
    db.commit()
    status = "verified" if user.is_verified else "unverified"
    return MessageResponse(message=f"Member {user.first_name} is now {status}")


@router.delete("/members/{user_id}", response_model=MessageResponse)
async def delete_member(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Remove a member."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return MessageResponse(message=f"User {user.email} deleted")


# ── Events ──

@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new event."""
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    data: EventUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update an existing event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", response_model=MessageResponse)
async def delete_event(
    event_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return MessageResponse(message=f"Event '{event.title}' deleted")


# ── Analytics ──

@router.get("/stats")
async def get_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get dashboard analytics for admins."""
    total_members = db.query(func.count(User.id)).scalar()
    verified_members = db.query(func.count(User.id)).filter(User.is_verified == True).scalar()
    total_events = db.query(func.count(Event.id)).scalar()
    total_registrations = db.query(func.count(EventRegistration.id)).scalar()

    # Branch breakdown
    branch_stats = (
        db.query(User.branch, func.count(User.id))
        .group_by(User.branch)
        .all()
    )

    return {
        "total_members": total_members,
        "verified_members": verified_members,
        "unverified_members": total_members - verified_members,
        "total_events": total_events,
        "total_event_registrations": total_registrations,
        "members_by_branch": {branch or "Unknown": count for branch, count in branch_stats},
    }


# ── Settings ──

from app.models import SystemSetting
from app.schemas import SettingResponse, SettingUpdate

@router.get("/settings", response_model=list[SettingResponse])
async def get_settings(
    db: Session = Depends(get_db),
):
    """Get all system settings. Not admin restricted so the public site can read them."""
    return db.query(SystemSetting).all()

@router.patch("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a system setting. Restricted to admins."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key, value=data.value)
        db.add(setting)
    else:
        setting.value = data.value
    db.commit()
    db.refresh(setting)
    return setting
