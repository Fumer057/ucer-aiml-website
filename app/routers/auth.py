"""Authentication routes: login, register, verify email."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse, MessageResponse
from app.auth import (
    hash_password, verify_password, create_access_token,
    create_verification_token, decode_verification_token,
    require_user,
)
from app.email_utils import send_verification_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user and send a verification email."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user
    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        phone=data.phone,
        branch=data.branch,
        year=data.year,
        roll_number=data.roll_number,
        area_of_interest=data.area_of_interest,
        is_verified=False,  # Manual verification required by admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send email only if it's the admin (other emails require domain verification on Resend free tier)
    if user.email == "rishabhshukla2901@gmail.com":
        token = create_verification_token(user.email)
        await send_verification_email(user.email, token)

    return MessageResponse(
        message="Application submitted! Please wait for admin approval.",
        detail=f"Registration for {user.email} is pending manual verification by an administrator.",
    )


@router.get("/verify", response_class=HTMLResponse)
async def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    """Verify a user's email via the token link sent in the email."""
    email = decode_verification_token(token)
    if not email:
        return HTMLResponse(
            content="""
            <html><body style="font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#F8F9FF;">
            <div style="text-align:center;"><h2>❌ Invalid or expired link</h2><p>Please request a new verification email.</p></div>
            </body></html>
            """,
            status_code=400,
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return HTMLResponse(
            content="<html><body><h2>User not found</h2></body></html>",
            status_code=404,
        )

    user.is_verified = True
    db.commit()

    return HTMLResponse(
        content=f"""
        <html><body style="font-family:'DM Sans',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#F8F9FF;">
        <div style="text-align:center;background:white;padding:48px;border-radius:16px;box-shadow:0 4px 24px rgba(67,97,238,0.08);">
            <h2 style="font-family:'Outfit',sans-serif;">✅ Email Verified!</h2>
            <p style="color:#6B7280;">Welcome to the UCER AIML Club, {user.first_name}!</p>
            <a href="/" style="display:inline-block;margin-top:16px;background:linear-gradient(135deg,#4361EE,#7209B7);color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:600;">Go to Home →</a>
        </div></body></html>
        """,
        status_code=200,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return a JWT access token."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_user)):
    """Get the currently authenticated user's profile."""
    return user
