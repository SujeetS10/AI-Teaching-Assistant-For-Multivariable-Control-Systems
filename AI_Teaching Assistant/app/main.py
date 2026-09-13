"""
FastAPI application entry point.

Responsible for: app creation, static/template setup, startup tasks,
and route registration. Actual endpoint logic lives in app/routes.py.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import SUBJECT_NAME, ADMIN_SESSION_SECRET, validate_config, ConfigError
from app.database import init_db
from app.routes import router, is_admin_session

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: fail fast with a clear message if configuration is missing,
    # and make sure the SQLite database/table exist.
    try:
        validate_config()
    except ConfigError as exc:
        print(f"[startup] Configuration error: {exc}")
        raise
    init_db()
    yield
    # No shutdown work needed for this simple project.


app = FastAPI(title="AI Teaching Assistant", lifespan=lifespan)

# Signs the admin login session cookie. See ADMIN_SESSION_SECRET in
# app/config.py for what happens if it isn't set in .env.
app.add_middleware(SessionMiddleware, secret_key=ADMIN_SESSION_SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def serve_frontend(request: Request):
    """Serve the single-page frontend with the fixed subject name."""
    # Modern Starlette signature: TemplateResponse(request, name, context).
    # "request" is passed as its own argument, not inside the context dict.
    return templates.TemplateResponse(
        request,
        "index.html",
        {"subject": SUBJECT_NAME},
    )


@app.get("/admin/login", response_class=HTMLResponse)
def serve_admin_login(request: Request):
    """
    Serve the admin login form. If already logged in, skip straight to
    the dashboard instead of showing the form again.
    """
    if is_admin_session(request):
        return RedirectResponse(url="/admin")
    show_error = request.query_params.get("error") == "1"
    return templates.TemplateResponse(
        request,
        "admin_login.html",
        {"subject": SUBJECT_NAME, "show_error": show_error},
    )


@app.get("/admin", response_class=HTMLResponse)
def serve_admin(request: Request):
    """
    Serve the admin dashboard page. Requires a logged-in session (see
    /admin/login) - anyone not logged in is redirected to the login form
    instead of seeing student data or a raw error.
    """
    if not is_admin_session(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse(
        request,
        "admin.html",
        {"subject": SUBJECT_NAME},
    )
