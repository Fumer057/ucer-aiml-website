"""Admin page routes — serves Jinja2 templates for the admin panel."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["admin-pages"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@router.get("/admin/members", response_class=HTMLResponse)
async def admin_members_page(request: Request):
    return templates.TemplateResponse("admin_members.html", {"request": request})


@router.get("/admin/events", response_class=HTMLResponse)
async def admin_events_page(request: Request):
    return templates.TemplateResponse("admin_events.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def member_dashboard_page(request: Request):
    return templates.TemplateResponse("member_dashboard.html", {"request": request})
