# CLAUDE.md

## Project Goal

Build a small, complete **AI Teaching Assistant web application** for a college
project.

The application must be restricted to **one subject only: Data Structures**.

The project should demonstrate how:

1. A student enters their registration number.
2. A student asks a question related to Data Structures.
3. A browser frontend sends the request to a Python backend.
4. The FastAPI backend sends the question to a hosted open-weight/open-source
   capable LLM through an API.
5. The model returns an answer.
6. The backend sends the answer back to the browser.
7. The interaction is stored in a local SQLite database.

This is primarily a classroom/college project. Keep the implementation
understandable and reasonably small, while still making it a complete working
web application.

The original reference `CLAUDE.md` emphasizes a small project, secure API-key
handling, a clear API → model → response flow, readable code, and avoiding
unnecessary complexity. Preserve those principles while adapting the project
to a FastAPI web application. Do not copy the reference's CLI-only scope,
because this project explicitly requires a frontend, backend, and database.

## Important Scope

### Subject restriction

The application must support **only Data Structures**.

Do not create:
- a subject dropdown
- multiple subject configurations
- subject selection from the browser
- separate pages for different subjects
- a generic "ask anything" mode

The backend must define the subject centrally, for example:

```text
SUBJECT_NAME=Data Structures
```

The frontend should display the fixed subject name, but must not be allowed
to change it.

The browser request should contain:
- registration number
- question

It should NOT contain a subject field.

The backend is responsible for assigning the configured subject to the
interaction.

### Technology scope

Use:

- Python 3.10+
- FastAPI
- Uvicorn
- HTML5
- CSS3
- vanilla JavaScript
- SQLite
- `python-dotenv`
- Hugging Face `huggingface_hub` / Inference Providers

Do not use:
- React
- Vue
- Angular
- Streamlit
- Flask
- Django
- Docker
- Kubernetes
- PostgreSQL
- MongoDB
- Redis
- vector databases
- RAG
- model training
- fine-tuning
- unnecessary frontend frameworks
- unnecessary backend frameworks

The frontend must communicate with the backend through FastAPI HTTP
endpoints.

## Application Architecture

Use this simple architecture:

```text
Student
   |
   v
Browser
HTML + CSS + JavaScript
   |
   | HTTP request
   v
FastAPI Backend
   |
   +----> SQLite database
   |
   | API request
   v
Hugging Face Inference API
   |
   v
Hosted LLM
   |
   | model response
   v
FastAPI Backend
   |
   v
Browser
```

The API key must remain on the backend.

Never expose the Hugging Face token to browser JavaScript.

## Project Structure

Create this structure:

```text
ai-teaching-assistant/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       └── llm_service.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```

Do not create extra files unless there is a clear technical reason.

The SQLite database file may be created automatically at runtime and should
not be manually populated.

## VS Code Execution Environment

This project is intended to be created and executed directly in **Visual
Studio Code**.

Claude Code should assume the user will:

1. Open the project folder in VS Code.
2. Open the integrated terminal.
3. Create a Python virtual environment.
4. Install the dependencies.
5. Create `.env` from `.env.example`.
6. Start the FastAPI server with Uvicorn.
7. Open the local application in a browser.

The project must work on Windows.

Prefer commands that work in the VS Code PowerShell terminal.

Also document the equivalent command for Command Prompt where useful.

Do not require Jupyter Notebook to run the application.

Jupyter may be used for experimentation, but it is not part of the final
application architecture.

## Environment Variables

Never put an API key directly in Python source code.

Create:

```text
.env.example
```

with:

```text
HF_TOKEN=your_huggingface_token_here
HF_MODEL=your_model_name_here
SUBJECT_NAME=Data Structures
```

The real `.env` file will contain the student's actual token.

The actual `.env` file must be included in `.gitignore`.

The application should fail with a clear, student-friendly error if the
Hugging Face token is missing.

Do not print the token.

Do not return the token through an API endpoint.

Do not place the token in HTML, CSS, or JavaScript.

Do not hard-code a model name if the current Hugging Face documentation
indicates that another model should be used. Keep the model configurable
through `HF_MODEL`.

## Hugging Face Integration

Use the official Python client/library supported by current Hugging Face
Inference Providers documentation.

Prefer:

```python
from huggingface_hub import InferenceClient
```

Initialize the client using the token loaded from the environment.

Use the current official chat-completion/API syntax documented by
Hugging Face at implementation time.

Do not invent SDK methods.

The LLM provider integration should be isolated in:

```text
app/services/llm_service.py
```

This keeps the FastAPI routes understandable.

The service should receive a student's Data Structures question and return
the model's answer as plain text.

The model should be configurable using:

```text
HF_MODEL
```

Do not expose the Hugging Face token to the frontend.

## AI Teaching Assistant Behavior

The system prompt should clearly establish that the model is a teaching
assistant for undergraduate **Data Structures**.

The assistant should:

- explain concepts clearly
- use simple language when appropriate
- provide examples
- explain algorithms step by step
- explain time and space complexity when relevant
- use pseudocode when useful
- help students understand rather than merely provide unexplained answers
- stay focused on Data Structures

Examples of supported topics include:

- arrays
- linked lists
- stacks
- queues
- trees
- binary search trees
- heaps
- hash tables
- graphs
- graph traversal
- BFS
- DFS
- sorting algorithms
- searching algorithms
- recursion
- Big-O notation
- time complexity
- space complexity

These are examples, not a requirement to build separate modules for every
topic.

## Subject Restriction in the AI Prompt

The application should instruct the model that it is restricted to Data
Structures.

If a student asks about an unrelated subject, the assistant should politely
state that it is designed specifically for Data Structures and encourage the
student to ask a Data Structures question.

Do not implement a complicated classifier or second AI call just to enforce
this restriction.

The backend-controlled subject and system prompt are sufficient for this
college project.

## Academic Integrity

The assistant should behave as a teaching assistant, not as a hidden
assignment-completion system.

When appropriate:
- explain reasoning
- show intermediate steps
- provide examples
- help debug a student's attempt
- encourage understanding

Do not make academic-integrity functionality unnecessarily complicated.

## Frontend Requirements

Use plain HTML, CSS, and JavaScript.

The main page should be clean, modern, simple, and suitable for a college
demonstration.

The page should visibly contain:

1. Application title
2. Fixed subject name: Data Structures
3. Registration number input
4. Question textarea
5. Ask button
6. Loading indicator
7. Answer display area
8. Clear/reset behavior

Suggested visual structure:

```text
+------------------------------------------------+
|              AI Teaching Assistant             |
|                 Data Structures                |
|                                                |
| Registration Number                            |
| [_______________________________]              |
|                                                |
| Ask your question                              |
| [                                            ] |
| [                                            ] |
| [                                            ] |
|                                                |
|                  [ Ask Question ]              |
|                                                |
| Answer                                         |
| ---------------------------------------------- |
| Model response appears here...                 |
+------------------------------------------------+
```

Do not use a frontend framework.

Do not put the API key in `app.js`.

## Registration Number

The registration number is required.

The frontend should reject an empty registration number.

Do not require a complicated authentication system.

For this college project, the registration number is an identifier for
stored interactions, not a password.

Trim leading/trailing whitespace.

Do not log the registration number unnecessarily in server logs.

## Question Input

The question is required.

Reject empty or whitespace-only questions.

Trim the question before processing.

A reasonable maximum question length should be enforced to prevent accidental
very large requests.

Use a simple validation limit such as 2000 characters unless there is a
clear reason to choose another value.

Return a clear validation error.

## FastAPI Backend

Use FastAPI as the communication layer between the browser and backend.

The main application should be created in:

```text
app/main.py
```

Use Uvicorn to run it.

The application should serve the frontend and expose the API.

Recommended endpoints:

```text
GET /
GET /health
POST /api/ask
```

### GET /

Serve:

```text
templates/index.html
```

The frontend's static files should be served from:

```text
/static
```

### GET /health

Return a simple JSON response showing that the backend is running.

For example:

```json
{
  "status": "ok"
}
```

Do not expose secrets or sensitive configuration.

### POST /api/ask

Accept JSON similar to:

```json
{
  "registration_no": "23CS001",
  "question": "Explain what a stack is."
}
```

Do NOT accept:

```json
{
  "subject": "Data Structures"
}
```

The subject is controlled by the backend.

The endpoint should:

1. Validate the registration number.
2. Validate the question.
3. Load the configured subject.
4. Send the question to the LLM service.
5. Store the interaction in SQLite.
6. Return the answer.

Return JSON similar to:

```json
{
  "answer": "A stack is a linear data structure...",
  "subject": "Data Structures"
}
```

Do not return:
- API keys
- internal exceptions
- unnecessary database details
- sensitive server configuration

## Pydantic Models

Use Pydantic models for request and response validation.

Create appropriate models in:

```text
app/models.py
```

At minimum, define a request model for:

```text
registration_no
question
```

and a response model for:

```text
answer
subject
```

Keep the models simple.

Do not create an excessive number of schemas.

## Database

Use SQLite.

The database exists to demonstrate that student interactions can be stored
with student details.

Create the database automatically when the application starts if it does not
exist.

Use a single interaction table.

Suggested table:

```text
interactions
```

Suggested columns:

```text
id
registration_no
subject
question
response
model_used
timestamp
```

Use a suitable SQLite type for each field.

The `id` should be an auto-incrementing primary key.

The timestamp should be generated by the application/database and should be
stored for every interaction.

The subject should always be the backend-controlled subject.

The model name should be stored so that the interaction records show which
configured model generated the response.

## Database Design Philosophy

Keep the database implementation simple enough for students to understand.

Do not introduce:
- SQLAlchemy unless it clearly improves the implementation without adding
  unnecessary complexity
- Alembic
- migrations
- repository patterns
- service layers solely for CRUD
- multiple database engines

A lightweight SQLite implementation is preferred.

If a small amount of direct SQL is used, make it readable and parameterized.

Never construct SQL by concatenating user input.

## Database File

The runtime database can be:

```text
database.db
```

or another clearly documented local SQLite filename.

Add the database file to `.gitignore` if it is generated locally.

Do not include real student interaction data in the repository.

## Database Service

Put database setup and basic interaction insertion in:

```text
app/database.py
```

It should provide simple functions such as:

- initialize database
- save interaction

Do not build a full ORM or generic database abstraction.

## Route Organization

Put API routes in:

```text
app/routes.py
```

Keep `main.py` responsible primarily for application creation,
configuration, static/template setup, and route registration.

Avoid putting all application logic into `main.py`.

## Configuration

Put environment/configuration handling in:

```text
app/config.py
```

Load `.env` using `python-dotenv`.

Expose simple configuration values such as:

```text
HF_TOKEN
HF_MODEL
SUBJECT_NAME
```

Fail clearly when required configuration is missing.

Do not expose secrets through the `/health` endpoint.

## Error Handling

Handle at least:

- missing Hugging Face token
- missing model configuration
- empty registration number
- empty question
- question too long
- Hugging Face/API/network errors
- unexpected LLM errors
- database errors

The user-facing error messages should be understandable.

Do not expose:
- stack traces to the browser
- API tokens
- internal credentials
- unnecessary provider internals

During development, errors may be logged in the terminal, but secrets must
never be logged.

## LLM Error Behavior

If the model API fails:

1. Do not insert a fake answer into the database.
2. Return a useful error response to the frontend.
3. Tell the student that the AI service is temporarily unavailable.
4. Log enough information for local debugging without exposing secrets.

Keep error handling simple.

## Frontend API Communication

The browser must use JavaScript `fetch()` to call:

```text
POST /api/ask
```

Do not call Hugging Face directly from JavaScript.

The flow must be:

```text
JavaScript
   |
   v
FastAPI /api/ask
   |
   v
Hugging Face
```

not:

```text
JavaScript
   |
   v
Hugging Face
```

This is important because the Hugging Face token must remain server-side.

## Frontend Behavior

When the user clicks "Ask Question":

1. Read registration number.
2. Read question.
3. Trim both.
4. Validate them.
5. Disable the Ask button while waiting.
6. Show a loading indicator.
7. Send JSON to `/api/ask`.
8. Receive JSON.
9. Display the answer.
10. Re-enable the button.
11. Display a clear error if the request fails.

Do not reload the page for every question.

Allow the user to ask another question after the first response.

## UI Design

The interface should be attractive but intentionally simple.

Use:
- centered main container
- clear labels
- comfortable spacing
- readable typography
- responsive layout
- visible focus states
- clear button states
- answer card
- loading state
- error message area

Do not use:
- external CSS frameworks
- external JavaScript frameworks
- unnecessary animations
- complicated component systems

The application should work reasonably well on both desktop and mobile
screens.

## Accessibility

Use semantic HTML.

Inputs should have labels.

Buttons should have meaningful text.

Do not rely on color alone to communicate errors.

Ensure reasonable keyboard navigation.

Use appropriate `aria` attributes where useful, but do not over-engineer
accessibility for this small project.

## Requirements

Create `requirements.txt`.

Include only packages actually required.

The project will need packages along the lines of:

```text
fastapi
uvicorn
python-dotenv
huggingface_hub
```

If an additional package is genuinely required by the final implementation,
include it and explain why.

Do not add packages merely for convenience.

Pin exact versions only if there is a demonstrated compatibility reason.
Otherwise use sensible package requirements compatible with current Python
versions.

## .gitignore

Include at least:

```text
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
database.db
```

Also ignore common local development artifacts if needed.

Never ignore source files.

## README.md

Create a student-friendly README.

It should explain:

### 1. What the project is

Explain that this is a Data Structures teaching assistant that demonstrates
communication between a browser, FastAPI backend, hosted LLM, and SQLite.

### 2. Architecture

Show:

```text
Browser
   |
   v
FastAPI
   |
   +----> SQLite
   |
   v
Hugging Face Inference API
   |
   v
LLM
```

### 3. Prerequisites

Mention:
- Python 3.10+
- VS Code
- internet connection
- Hugging Face account/token

### 4. Create virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 5. Install dependencies

```text
pip install -r requirements.txt
```

### 6. Configure environment

Explain how to copy:

```text
.env.example
```

to:

```text
.env
```

Then fill in:

```text
HF_TOKEN=...
HF_MODEL=...
SUBJECT_NAME=Data Structures
```

Do not include a real token in the README.

### 7. Run the application

Use:

```text
uvicorn app.main:app --reload
```

Then tell the user to open the local URL printed by Uvicorn, normally:

```text
http://127.0.0.1:8000
```

Do not hard-code a claim that another port will be used unless the project
actually configures one.

### 8. API documentation

Mention that FastAPI normally provides interactive documentation at:

```text
/docs
```

Do not require students to use it for the normal application flow.

### 9. Database

Explain that interactions are automatically stored in the local SQLite
database.

### 10. Security

Explicitly warn:

- Never commit `.env`.
- Never commit the Hugging Face token.
- Never put the token in frontend JavaScript.
- Never hard-code the token.
- If a token is accidentally exposed, revoke it and create a new one.

### 11. Troubleshooting

Include simple troubleshooting for:
- Python not found
- virtual environment activation problems
- missing HF_TOKEN
- invalid/expired HF token
- invalid model
- network/API errors
- port already in use
- database creation problems

Do not invent provider-specific error codes.

## Testing

Create:

```text
tests/test_api.py
```

Tests should focus on the backend behavior.

At minimum test:

1. `/health` returns success.
2. Empty registration number is rejected.
3. Empty question is rejected.
4. A valid request can be processed when the LLM call is mocked.
5. A successful interaction is stored in SQLite when the LLM call is mocked.

Do NOT make automated tests depend on a real Hugging Face API call.

The tests should mock the LLM service.

Keep testing straightforward.

If `pytest` is needed, include it in `requirements.txt` or clearly document
it as a development dependency.

## No Real API Calls in Tests

This is important.

Never require a real Hugging Face token for unit tests.

Tests must be runnable even if:
- the user has no internet connection
- the user has no Hugging Face credits
- the model is temporarily unavailable

Mock the AI service.

## FastAPI Startup

Initialize the SQLite database when the application starts.

Avoid deprecated FastAPI patterns if current documentation recommends a newer
startup/lifespan approach.

Use the current stable FastAPI approach available at implementation time.

Do not add complex startup infrastructure.

## CORS

Do not add CORS middleware unless it is actually required.

Because the frontend is served by the same FastAPI application, the normal
application flow should use same-origin requests.

If CORS is added for a real technical reason, explain why in the README.

## Templates and Static Files

Use FastAPI/Starlette mechanisms to serve:

```text
templates/index.html
static/style.css
static/app.js
```

The HTML should not contain the Hugging Face token.

The JavaScript should only communicate with the FastAPI API.

## API Response Format

Keep the API response simple.

Successful response:

```json
{
  "answer": "string",
  "subject": "Data Structures"
}
```

Validation/error responses should follow normal FastAPI behavior where
appropriate.

Do not create a custom response envelope unless necessary.

## Data Flow

The complete request flow should be:

```text
1. Student opens browser
2. Browser requests GET /
3. FastAPI serves index.html
4. Browser loads CSS and JavaScript
5. Student enters registration number
6. Student enters Data Structures question
7. JavaScript validates the inputs
8. JavaScript POSTs /api/ask
9. FastAPI validates request
10. FastAPI loads subject configuration
11. FastAPI calls llm_service
12. llm_service calls Hugging Face
13. Hugging Face returns model response
14. FastAPI saves the interaction in SQLite
15. FastAPI returns JSON
16. JavaScript displays the answer
```

Keep this flow easy to understand in the source code.

## Code Quality

The code should be:

- readable
- beginner-friendly
- reasonably short
- appropriately commented
- easy to run from VS Code
- easy to explain during a college project demonstration
- easy to modify with Claude Code

Comments should explain important logic, not every obvious line.

Avoid:
- unnecessary classes
- excessive abstraction
- dependency injection complexity beyond what FastAPI naturally uses
- design patterns for their own sake
- complicated logging frameworks
- unnecessary async complexity
- generic CRUD frameworks

Async FastAPI endpoints are allowed where they make sense, but do not add
async complexity solely for appearance.

## Security Rules

The following are mandatory:

1. The Hugging Face token exists only on the backend.
2. The `.env` file is ignored by Git.
3. No secret appears in frontend files.
4. No secret appears in API responses.
5. No secret appears in error messages.
6. User input is validated.
7. Database queries use parameterized values.
8. No raw user input is inserted into SQL strings.
9. No real student data is included in the repository.
10. Do not add authentication unless explicitly requested later.

This is a classroom project, not a production security system. Do not claim
that it provides enterprise-grade security.

## Subject Display

The UI should make the fixed scope obvious.

For example:

```text
AI Teaching Assistant
Data Structures
```

The subject can also appear in the answer area.

Do not provide a control that allows students to change the subject.

## Prompt Injection Awareness

The application should not assume that every instruction inside a student's
question is trustworthy.

The system prompt should establish the assistant's role and subject scope.

Do not build a sophisticated prompt-injection defense system for this
project.

The goal is a clear teaching application, not a security research system.

## Logging

Use minimal logging.

Do not log:
- Hugging Face tokens
- full environment configuration
- unnecessary sensitive student information

If an error needs to be debugged, log a concise technical message.

Do not add a large observability stack.

## Claude Code Workflow

When executing this `CLAUDE.md` with Claude Code, follow this order:

### Phase 1 — Inspect

1. Read this entire `CLAUDE.md`.
2. Inspect the existing project directory.
3. Do not overwrite unrelated user files.
4. If an existing implementation is present, preserve useful work unless it
   conflicts with this specification.

### Phase 2 — Plan

Before writing code, briefly identify:
- files to create
- FastAPI flow
- database approach
- Hugging Face integration
- frontend flow
- testing approach

Do not spend excessive effort on architecture documents.

### Phase 3 — Implement

Create the project structure.

Implement:
1. configuration
2. database
3. models
4. LLM service
5. routes
6. FastAPI app
7. HTML
8. CSS
9. JavaScript
10. tests
11. README
12. requirements
13. `.env.example`
14. `.gitignore`

### Phase 4 — Verify

Run:
- dependency installation where appropriate
- syntax/import checks
- tests
- FastAPI startup check if practical

Do not make a real LLM API call merely to run unit tests.

If a real API call is needed for final manual verification, clearly identify
that it requires the user's own Hugging Face token and available provider
credits.

### Phase 5 — Explain

After implementation, provide a concise summary of:
- what was created
- how to start it in VS Code
- where the `.env` file goes
- how the browser talks to FastAPI
- where interactions are stored
- how to run tests

Do not overwhelm the user with implementation details unless requested.

## VS Code Run Instructions

The final project should support this normal workflow:

```powershell
cd ai-teaching-assistant

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

If PowerShell blocks virtual-environment activation, document a safe
alternative using Command Prompt rather than requiring users to change
system-wide execution policies unnecessarily.

## Manual Demonstration

The application should be easy to demonstrate in a college presentation.

Recommended demonstration:

### Step 1

Open the website.

Show:

```text
AI Teaching Assistant
Data Structures
```

### Step 2

Enter a sample registration number.

### Step 3

Ask:

```text
Explain what a stack is and give a real-world example.
```

### Step 4

Show the AI response.

### Step 5

Ask a second question:

```text
What is the time complexity of binary search and why?
```

### Step 6

Show that the application can answer multiple Data Structures questions.

### Step 7

Explain that each interaction is stored in SQLite with:
- registration number
- subject
- question
- response
- model
- timestamp

### Step 8

Show the high-level architecture:

```text
Browser
   ↓
FastAPI
   ↓
Hugging Face API
   ↓
LLM
   ↓
FastAPI
   ↓
Browser

FastAPI
   ↓
SQLite
```

## Do Not Over-engineer

This is a college project.

Do not add:
- authentication
- user accounts
- password systems
- admin dashboards
- chat history UI
- multiple subjects
- RAG
- vector databases
- document upload
- embeddings
- model training
- fine-tuning
- Docker
- Kubernetes
- React
- complex state management
- microservices
- cloud deployment
- payment systems
- production monitoring
- unnecessary API abstractions

These may be future extensions, but they are outside the initial scope.

## Future Extensions

Mention these only as possible future improvements in the README or final
summary. Do not implement them unless explicitly requested:

- student login
- interaction history
- admin dashboard
- multiple subjects
- teacher-provided notes
- RAG over course material
- local Ollama model
- deployment to a cloud service
- analytics
- feedback/rating system

## Definition of Done

The project is complete when all of the following are true:

- [ ] The project opens cleanly in VS Code.
- [ ] A Python virtual environment can be created.
- [ ] Dependencies install successfully.
- [ ] `.env.example` exists.
- [ ] `.env` is ignored by Git.
- [ ] The application is restricted to Data Structures.
- [ ] The browser cannot select another subject.
- [ ] FastAPI serves the frontend.
- [ ] `/health` works.
- [ ] `/api/ask` validates input.
- [ ] `/api/ask` calls the LLM service.
- [ ] The Hugging Face token stays server-side.
- [ ] The model is configurable.
- [ ] Successful interactions are stored in SQLite.
- [ ] The frontend displays the model response.
- [ ] Loading and error states work.
- [ ] Unit tests do not require a real LLM API call.
- [ ] README explains setup and execution in VS Code.
- [ ] No unnecessary frameworks or services were added.
- [ ] The application can be demonstrated live in a browser.

## Final Principle

The central idea of this project is:

**"A student can ask a Data Structures question in a browser, FastAPI can
send it securely to a hosted LLM, and the application can return and store
the response."**

Keep the implementation simple enough for a college student to understand,
but complete enough to function as a real web application.

When in doubt, prefer the simplest implementation that satisfies this
`CLAUDE.md`.
