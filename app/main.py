"""
UCER AIML Club — FastAPI Application Entry Point

Run with: uvicorn app.main:app --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routers import auth, events, admin, pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_tables()

    # Migration: Add missing columns if they don't exist
    from sqlalchemy import text
    from app.database import engine
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS area_of_interest VARCHAR(100)"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE"))
    except Exception as e:
        print(f"Migration error: {e}")

    print("\n[STARTED] UCER AIML Club API is running!")
    print("   [PAGE] Landing page: http://localhost:8000")
    print("   [DOCS] API docs:     http://localhost:8000/docs")
    print("   [ADMIN] Admin panel:  http://localhost:8000/admin")
    print("   [USER] Dashboard:    http://localhost:8000/dashboard\n")
    yield


app = FastAPI(
    title="UCER AIML Club API",
    description="Backend API for the UCER AIML Club website — registration, events, and admin management.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend requests from any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routers ──
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(pages.router)

# ── Serve the static landing page ──
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

# Create static dir if it doesn't exist
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
async def serve_landing_page():
    """Serve the main landing page."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    # Fallback to the existing file name
    alt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "ucer-aiml-landing.html",
    )
    if os.path.exists(alt_path):
        return FileResponse(alt_path)
    return JSONResponse(
        {"message": "Welcome to the UCER AIML Club API. Visit /docs for API documentation."}
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ucer-aiml-club-api"}
