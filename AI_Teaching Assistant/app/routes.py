"""
API routes.

Kept separate from main.py so the FastAPI app-creation code stays clean.
"""

import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import SUBJECT_NAME, GROQ_MODEL, ADMIN_USERNAME, ADMIN_PASSWORD
from app.database import save_interaction, get_all_interactions, set_resolved
from app.models import AskRequest, AskResponse, InteractionOut, ResolveRequest
from app.services.llm_service import get_answer, LLMServiceError

router = APIRouter()


def is_admin_session(request: Request) -> bool:
    """True if this request's signed session cookie marks it as logged in."""
    return bool(request.session.get("is_admin"))


def require_admin_api(request: Request) -> None:
    """
    Dependency for /api/admin/* JSON endpoints. Raises a plain 401 JSON
    error (these are called by fetch(), not a browser navigation, so a
    redirect wouldn't make sense here).
    """
    if not is_admin_session(request):
        raise HTTPException(status_code=401, detail="Not logged in as admin.")


@router.get("/health")
def health_check():
    """Simple check that the backend is running. No secrets returned."""
    return {"status": "ok"}


@router.post("/api/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    """
    Receive a student's registration number and question, get an answer
    from the LLM, store the interaction, and return the answer.

    The subject is NOT accepted from the browser - it is always the
    backend-configured SUBJECT_NAME.
    """
    try:
        answer = get_answer(payload.question)
    except LLMServiceError as exc:
        # 503 = service temporarily unavailable. No internal details leaked.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        save_interaction(
            registration_no=payload.registration_no,
            subject=SUBJECT_NAME,
            question=payload.question,
            response=answer,
            model_used=GROQ_MODEL,
        )
    except Exception as exc:  # noqa: BLE001
        # The student already has a valid answer - a storage failure
        # shouldn't block the response, but we log it locally.
        print(f"[routes] Failed to save interaction: {type(exc).__name__}")

    return AskResponse(answer=answer, subject=SUBJECT_NAME)


@router.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Check submitted credentials and, if correct, mark this session as an
    admin session via a signed cookie. Redirects back to /admin either way
    (with an error flag on failure) since this is a plain HTML form POST,
    not a fetch() call.
    """
    correct_username = secrets.compare_digest(username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(password, ADMIN_PASSWORD or "")

    if correct_username and correct_password:
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin", status_code=303)

    return RedirectResponse(url="/admin/login?error=1", status_code=303)


@router.get("/admin/logout")
def admin_logout(request: Request):
    """Clear the session and send the admin back to the login page."""
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get("/api/admin/interactions", response_model=list[InteractionOut])
def list_interactions(_: None = Depends(require_admin_api)):
    """Return every stored student interaction, most recent first."""
    rows = get_all_interactions()
    return [
        InteractionOut(
            id=row["id"],
            registration_no=row["registration_no"],
            subject=row["subject"],
            question=row["question"],
            response=row["response"],
            model_used=row["model_used"],
            timestamp=row["timestamp"],
            resolved=bool(row["resolved"]),
        )
        for row in rows
    ]


@router.patch("/api/admin/interactions/{interaction_id}", response_model=dict)
def update_interaction(
    interaction_id: int,
    payload: ResolveRequest,
    _: None = Depends(require_admin_api),
):
    """Mark one interaction resolved or unresolved."""
    updated = set_resolved(interaction_id, payload.resolved)
    if not updated:
        raise HTTPException(status_code=404, detail="Interaction not found.")
    return {"id": interaction_id, "resolved": payload.resolved}
