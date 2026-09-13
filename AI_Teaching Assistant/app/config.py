"""
Application configuration.

Loads settings from a local .env file using python-dotenv and exposes
them as simple module-level values. Keeping configuration in one place
makes it easy to see everything the app depends on.
"""

import os
import secrets
from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present).
load_dotenv()

# --- Subject (fixed, backend-controlled) -----------------------------------
# This app is intentionally restricted to ONE subject. The frontend has no
# way to change it; students only ever see and use this value.
SUBJECT_NAME = os.getenv("SUBJECT_NAME", "Multivariable Control Systems")

# --- Groq configuration ------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# --- Question length limit ---------------------------------------------------
MAX_QUESTION_LENGTH = 2000

# --- Admin dashboard credentials -----------------------------------------------
# Protects /admin behind a login page + signed session cookie (not HTTP
# Basic Auth - browser support for Basic Auth's native login popup is
# inconsistent, so a real login form is more reliable).
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Signs the session cookie. If not set in .env, a random one is generated
# at startup - sessions just won't survive a server restart in that case
# (you'll need to log in again), which is fine for local/classroom use.
# Set ADMIN_SESSION_SECRET in .env for sessions that persist across restarts.
ADMIN_SESSION_SECRET = os.getenv("ADMIN_SESSION_SECRET") or secrets.token_hex(32)


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def validate_config() -> None:
    """
    Check that required configuration is present.

    Called on startup so the app fails fast with a clear, student-friendly
    error instead of a confusing failure the first time a question is asked.
    """
    if not GROQ_API_KEY:
        raise ConfigError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and set your "
            "Groq API key (GROQ_API_KEY=...). Get one free at "
            "console.groq.com/keys."
        )
    if not ADMIN_PASSWORD:
        raise ConfigError(
            "ADMIN_PASSWORD is missing. Copy .env.example to .env and set a "
            "password for the /admin dashboard (ADMIN_PASSWORD=...). Pick "
            "your own password - this protects student data from being "
            "viewed by anyone who finds the URL."
        )
