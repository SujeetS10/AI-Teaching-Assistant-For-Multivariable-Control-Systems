"""
Backend tests.

The LLM service is mocked throughout, so these tests never require a real
Hugging Face token, internet access, or provider credits.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Make sure required env vars exist before app.config is imported, so
# validate_config() doesn't fail during test collection.
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("GROQ_MODEL", "test-model")
os.environ.setdefault("SUBJECT_NAME", "Multivariable Control Systems")
os.environ.setdefault("ADMIN_USERNAME", "test-admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app import database as db  # noqa: E402

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_registration_number_rejected():
    response = client.post(
        "/api/ask",
        json={"registration_no": "   ", "question": "What is a stack?"},
    )
    assert response.status_code == 422


def test_empty_question_rejected():
    response = client.post(
        "/api/ask",
        json={"registration_no": "23EE0142", "question": "   "},
    )
    assert response.status_code == 422


@patch("app.routes.get_answer")
def test_valid_request_returns_answer(mock_get_answer):
    mock_get_answer.return_value = "Controllability means every state can be reached."

    response = client.post(
        "/api/ask",
        json={
            "registration_no": "23EE0142",
            "question": "What is controllability?",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Controllability means every state can be reached."
    assert data["subject"] == "Multivariable Control Systems"


@patch("app.routes.get_answer")
def test_interaction_is_stored_in_database(mock_get_answer, tmp_path, monkeypatch):
    mock_get_answer.return_value = "A state-space model uses matrices A, B, C, D."

    # Point the database module at a temporary file for this test only.
    test_db_path = tmp_path / "test_database.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_db()

    response = client.post(
        "/api/ask",
        json={
            "registration_no": "23EE0142",
            "question": "What is a state-space model?",
        },
    )
    assert response.status_code == 200

    with db.get_connection() as conn:
        rows = conn.execute("SELECT registration_no, question, response FROM interactions").fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "23EE0142"
    assert rows[0][1] == "What is a state-space model?"
    assert rows[0][2] == "A state-space model uses matrices A, B, C, D."


def admin_login(test_client, *, username="test-admin", password="test-admin-password"):
    """Log the given TestClient in as admin. Cookies persist on the client
    afterwards, the same way a browser session would."""
    return test_client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_admin_login_page_loads():
    response = client.get("/admin/login")
    assert response.status_code == 200


def test_admin_page_redirects_when_not_logged_in():
    fresh_client = TestClient(app)
    response = fresh_client.get("/admin", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/admin/login"


def test_admin_endpoints_reject_no_session():
    fresh_client = TestClient(app)
    response = fresh_client.get("/api/admin/interactions")
    assert response.status_code == 401


def test_admin_login_wrong_credentials_redirects_with_error():
    fresh_client = TestClient(app)
    response = admin_login(fresh_client, password="wrong-password")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login?error=1"
    # A failed login must not grant a session.
    api_response = fresh_client.get("/api/admin/interactions")
    assert api_response.status_code == 401


def test_admin_login_correct_credentials_grants_session():
    fresh_client = TestClient(app)
    login_response = admin_login(fresh_client)
    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/admin"

    # The session cookie now persists on this client for later requests.
    dashboard_response = fresh_client.get("/admin")
    assert dashboard_response.status_code == 200


@patch("app.routes.get_answer")
def test_admin_can_list_and_resolve_interaction(mock_get_answer, tmp_path, monkeypatch):
    mock_get_answer.return_value = "LQR minimizes a quadratic cost function."
    test_db_path = tmp_path / "test_database_admin.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_db()

    ask_response = client.post(
        "/api/ask",
        json={"registration_no": "23EE0142", "question": "What is LQR?"},
    )
    assert ask_response.status_code == 200

    admin_client = TestClient(app)
    admin_login(admin_client)

    list_response = admin_client.get("/api/admin/interactions")
    assert list_response.status_code == 200
    interactions = list_response.json()
    assert len(interactions) == 1
    assert interactions[0]["registration_no"] == "23EE0142"
    assert interactions[0]["resolved"] is False

    interaction_id = interactions[0]["id"]
    resolve_response = admin_client.patch(
        f"/api/admin/interactions/{interaction_id}",
        json={"resolved": True},
    )
    assert resolve_response.status_code == 200

    list_response_after = admin_client.get("/api/admin/interactions")
    assert list_response_after.json()[0]["resolved"] is True


def test_admin_resolve_unknown_interaction_returns_404(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_database_admin_404.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_db()

    admin_client = TestClient(app)
    admin_login(admin_client)

    response = admin_client.patch(
        "/api/admin/interactions/9999",
        json={"resolved": True},
    )
    assert response.status_code == 404


def test_admin_logout_clears_session():
    admin_client = TestClient(app)
    admin_login(admin_client)
    assert admin_client.get("/api/admin/interactions").status_code == 200

    admin_client.get("/admin/logout", follow_redirects=False)

    assert admin_client.get("/api/admin/interactions").status_code == 401
