# AI Teaching Assistant — Multivariable Control Systems

A small, complete web application that acts as an AI teaching assistant for
one subject only: **Multivariable Control Systems**. A student enters a
registration number and a question in the browser, the FastAPI backend sends
the question to a hosted LLM through the Groq API, the
answer is returned to the browser, and every interaction is stored in a
local SQLite database.

## 1. What this project is

This app demonstrates a full request/response loop:

Browser → FastAPI backend → Groq API → LLM → FastAPI → Browser,
with every interaction also saved to SQLite.

The subject is fixed in the backend configuration. There is no subject
selector anywhere in the UI, and the browser cannot send a subject — the
backend always assigns `SUBJECT_NAME` to each interaction.

## 2. Architecture

```text
Browser
   |
   v
FastAPI  (app/main.py, app/routes.py)
   |
   +----> SQLite (app/database.py)
   |
   v
Groq API (app/services/llm_service.py)
   |
   v
Hosted LLM
```

## 3. Prerequisites

- Python 3.10 or newer
- Visual Studio Code (recommended)
- An internet connection
- A Groq account and API key (https://console.groq.com/keys)

## 4. Create a virtual environment

Open the project folder in VS Code, then open the integrated terminal.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

If PowerShell blocks activation with an execution-policy error, use the
Command Prompt version instead rather than changing system-wide policies.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure your environment

Copy `.env.example` to `.env`:

```bash
copy .env.example .env        # Command Prompt
Copy-Item .env.example .env   # PowerShell
cp .env.example .env          # macOS / Linux
```

Then open `.env` and fill in your own values:

```text
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
SUBJECT_NAME=Multivariable Control Systems
ADMIN_USERNAME=admin
ADMIN_PASSWORD=pick_your_own_password
```

`ADMIN_USERNAME`/`ADMIN_PASSWORD` protect the `/admin` dashboard (see
section 9 below). Pick your own password — don't leave the example value.

Never commit `.env` — it is already listed in `.gitignore`. Never put your
token in the README, in `app.js`, or anywhere in the frontend.

## 7. Run the application

```bash
uvicorn app.main:app --reload
```

Then open the URL Uvicorn prints, normally:

```text
http://127.0.0.1:8000
```

## 8. API documentation

FastAPI automatically provides interactive docs at `/docs`. This is useful
for exploring the API but isn't needed for the normal student flow — the
web page at `/` is the intended way to use the app.

## 9. Admin dashboard

Open `http://127.0.0.1:8000/admin` in a browser. You'll land on a login
page — enter the `ADMIN_USERNAME` / `ADMIN_PASSWORD` values from your
`.env`. Once logged in, your session stays active (via a cookie) until you
click "Log out" or restart the server (see the note on
`ADMIN_SESSION_SECRET` in `.env.example` if you want sessions to survive
restarts).

The dashboard shows every question a student has asked, in a table with:

- **Status** — an Unresolved/Resolved toggle button. Click it to flip the
  status for that interaction (e.g. once a query is settled in office
  hours or a follow-up discussion).
- **Reg. No.** — the student's registration number.
- **Question** / **Answer** — truncated previews; click anywhere on a row
  to open the full question and answer (rendered with the same
  Markdown/math formatting as the student page) in a popup.
- **Asked** — when the question was submitted.

Use the "Hide resolved" checkbox to see only outstanding doubts, and
"Refresh" to pull in newly submitted questions without reloading the page.

This is protected by a login form and a signed session cookie using the
credentials in `.env` — it is not indexed or linked from the student page,
but anyone with the URL and correct password can view all stored student
questions, so keep the password private and don't share it in chat,
screenshots, or commit it to version control.

## 10. Database

Every successful question/answer pair is stored automatically in a local
SQLite file, `database.db`, created the first time the app runs. Each row
records: registration number, subject, question, response, model used, a
timestamp, and a resolved flag (0/1) used by the admin dashboard. This file
is not committed to version control. If you already had a `database.db`
from before the admin dashboard was added, it's automatically upgraded in
place the next time the app starts — no data is lost.

## 11. Security notes

- The Groq API key lives only on the backend (`app/config.py`,
  read from `.env`) and is never sent to the browser or returned by any
  endpoint.
- `.env` is git-ignored — never commit it.
- If a token is ever accidentally exposed, revoke it in your Groq console and
  generate a new one.
- The `/admin` dashboard and its API endpoints require a login (see
  section 9) using `ADMIN_USERNAME`/`ADMIN_PASSWORD` from `.env`.
  Credentials are compared with a constant-time comparison
  (`secrets.compare_digest`) to avoid leaking timing information, and the
  session cookie is cryptographically signed (via `ADMIN_SESSION_SECRET`)
  so it can't be forged or tampered with.
- Database queries use parameterized SQL — user input is never concatenated
  into a SQL string.
- This is a classroom project, not a production security system. The
  session cookie is sent with every request to this site (standard
  cookie behavior) — fine for local/classroom use over `http://127.0.0.1`,
  but if you ever deploy this somewhere publicly reachable, put it behind
  HTTPS and set a real `ADMIN_SESSION_SECRET` so login sessions aren't
  sent in the clear or invalidated on every restart. The registration
  number itself is a student identifier, not a password.


## 12. Troubleshooting

| Problem | What to check |
|---|---|
| `python` not found | Make sure Python 3.10+ is installed and on your PATH. Try `python3` on macOS/Linux. |
| Virtual environment won't activate (PowerShell) | Use the Command Prompt activation command instead of changing execution policy. |
| Server fails on startup mentioning `GROQ_API_KEY` | You haven't created `.env`, or it's missing `GROQ_API_KEY`. Copy `.env.example` to `.env` and fill it in. |
| "AI service is temporarily unavailable" | Your `GROQ_API_KEY` may be invalid/expired, `GROQ_MODEL` may be wrong, or there's a network issue. Check your `.env` values. |
| Port already in use | Run `uvicorn app.main:app --reload --port 8001` and open that port instead. |
| Database errors on startup | Make sure the app has permission to write a file in the project folder; delete `database.db` and restart if it becomes corrupted. |

## 13. Running tests

Tests mock the LLM service, so they run without a real Groq API key,
internet access, or API credits:

```bash
pytest
```

## Project structure

```text
mcs-teaching-assistant/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── main.py            FastAPI app, static/template setup, startup
│   ├── config.py          Environment/config loading
│   ├── database.py        SQLite setup, save/list/resolve interactions
│   ├── models.py          Pydantic request/response models
│   ├── routes.py          /health, /api/ask, /api/admin/*
│   └── services/
│       └── llm_service.py Groq integration + system prompt
├── templates/
│   ├── index.html         Student-facing page
│   ├── admin_login.html   Admin login form
│   └── admin.html         Admin dashboard page
├── static/
│   ├── style.css          Shared theme
│   ├── app.js             Student page logic
│   ├── admin.css          Admin dashboard styling
│   └── admin.js           Admin dashboard logic
└── tests/
    └── test_api.py
```

## Future extensions (not implemented)

Possible next steps, out of scope for this version: student login,
interaction history per student, an admin dashboard, teacher-provided notes
or RAG over course material, a local Ollama model option, deployment to a
cloud service, and a feedback/rating system.
