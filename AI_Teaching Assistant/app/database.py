"""
Lightweight SQLite storage for student interactions.

No ORM, no migrations framework - just small, explicit helper functions.
This keeps the database layer easy to read and explain in a college
project demo.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection() -> sqlite3.Connection:
    """Open a new connection to the SQLite database file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the interactions table if it does not already exist, and add
    the "resolved" column to any pre-existing database that predates it
    (so upgrading the app doesn't lose or break an existing database.db).
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_no TEXT NOT NULL,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                model_used TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                resolved INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        # Older database.db files (created before "resolved" existed) won't
        # have this column yet - add it if it's missing.
        existing_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(interactions)")
        }
        if "resolved" not in existing_columns:
            conn.execute(
                "ALTER TABLE interactions ADD COLUMN resolved INTEGER NOT NULL DEFAULT 0"
            )
        conn.commit()


def save_interaction(
    registration_no: str,
    subject: str,
    question: str,
    response: str,
    model_used: str,
) -> None:
    """
    Store one student interaction. New interactions start as unresolved.

    Uses parameterized SQL (the "?" placeholders) so user input is never
    concatenated directly into a SQL string.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO interactions
                (registration_no, subject, question, response, model_used, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (registration_no, subject, question, response, model_used, timestamp),
        )
        conn.commit()


def get_all_interactions() -> list[dict[str, Any]]:
    """Return every stored interaction, most recent first, for the admin view."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, registration_no, subject, question, response,
                   model_used, timestamp, resolved
            FROM interactions
            ORDER BY id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def set_resolved(interaction_id: int, resolved: bool) -> bool:
    """
    Mark one interaction resolved/unresolved. Returns True if a row was
    updated, False if no interaction with that id exists.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE interactions SET resolved = ? WHERE id = ?",
            (1 if resolved else 0, interaction_id),
        )
        conn.commit()
        return cursor.rowcount > 0
