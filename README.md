# Disaster Triage Response API

A FastAPI backend for registering users and reporting and managing disaster incidents. The API stores users and incidents in PostgreSQL using SQLAlchemy, with Alembic migrations. Authenticated users can report incidents, view published incidents, and manage incidents they reported.

> This is a learning and portfolio project. It is not a certified emergency dispatch or life-safety service.

## Features

- User registration with email, phone number, and password.
- Password hashing before credentials are stored.
- OAuth2 password-form login that returns a JWT bearer token.
- Role-aware user access for citizens, responders, and administrators.
- Incident creation, listing, retrieval, updating, and deletion.
- PostgreSQL persistence and Alembic database migrations.
- Interactive API documentation from FastAPI.

## Requirements

- Python 3.14 or later (as declared in `pyproject.toml`).
- PostgreSQL.
- `uv` to install the locked project dependencies, or another compatible Python package workflow.

## Setup

From the project directory, create and activate a virtual environment and install dependencies:

```powershell
uv sync
.venv\Scripts\Activate.ps1
```

Create a PostgreSQL database, then copy `.env.example` to `.env` and set the values for your local database and token configuration. Keep `.env` private and do not commit real credentials or signing keys.

Required settings:

| Variable | Purpose |
| --- | --- |
| `DATABASE_USER` | PostgreSQL username |
| `DATABASE_PASSWORD` | PostgreSQL password |
| `DATABASE_HOST` | PostgreSQL host name |
| `DATABASE_PORT` | PostgreSQL port |
| `DATABASE_NAME` | Database name |
| `SECRET_KEY` | Secret used to sign JWT access tokens |
| `ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_MINUTES` | Access-token lifetime in minutes |

Apply the database migrations:

```powershell
alembic -c alembic.ini upgrade head
```

Start the development server:

```powershell
fastapi dev main.py
```

The service is available at <http://127.0.0.1:8000>. Interactive API docs are at <http://127.0.0.1:8000/docs> and the alternative docs UI is at <http://127.0.0.1:8000/redoc>.

## API routes

All incident routes require a valid bearer token. The user lookup route also requires the administrator role.

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/home` | None | Return a welcome message |
| `POST` | `/users/` | None | Register a citizen account |
| `GET` | `/users/{user_id}` | Admin | Get a user's public profile |
| `POST` | `/login/` | Form credentials | Verify credentials and return an access token |
| `GET` | `/incidents/` | Bearer token | List published incidents |
| `GET` | `/incidents/{incident_id}` | Bearer token | Get a published incident |
| `POST` | `/incidents/` | Bearer token | Report an incident as the current user |
| `PATCH` | `/incidents/{incident_id}` | Bearer token | Update an incident reported by the current user |
| `DELETE` | `/incidents/{incident_id}` | Bearer token | Delete an incident reported by the current user or by an admin |

The current implementation returns `404` when an incident cannot be found. Listing incidents also returns `404` when there are no published incidents. Updates return `400` if no fields are provided and `403` if the current user does not own the incident.

## Authentication

Register an account with `POST /users/` using JSON:

```json
{
  "user_fullname": "Alex Example",
  "user_phoneno": "+919876543210",
  "user_email": "alex@example.com",
  "user_password": "choose-a-strong-password"
}
```

New accounts receive the `citizen` role. Login at `POST /login/` using form fields named `username` (the account email) and `password`. The response contains an access token and token type:

```json
{
  "access_token": "<access-token>",
  "token_type": "bearer",
  "role": "citizen"
}
```

In Swagger UI, use **Authorize** and enter the token as a bearer credential. For direct requests, send:

```text
Authorization: Bearer <access-token>
```

## Reporting an incident

Send `POST /incidents/` with a bearer token and JSON body:

```json
{
  "incident_type": "Flood",
  "description": "Rising water reported near the east bridge.",
  "severity": "low",
  "published": true
}
```

The API assigns the incident ID, report timestamp, and reporter from the authenticated account. The response also includes the reporter's public profile. `severity` defaults to `low` and `published` defaults to `true` if omitted.

## Project structure

```text
main.py                         FastAPI application entry point
backend/app/api/v1/endpoints/   Authentication, user, and incident routes
backend/core/                   Settings, password hashing, and JWT helpers
backend/database/               SQLAlchemy engine and request-scoped sessions
backend/models/                 SQLAlchemy database models
backend/schemas/                Pydantic request and response schemas
backend/alembic/                Database migration environment and revisions
```

## Current limitations

- The API currently has no pagination or filtering for incident lists.
- Incident severity is represented as a string, and the API does not yet implement a responder assignment or incident status workflow.
- The API currently exposes only published incidents through the list and detail routes.
- Authentication uses bearer access tokens; there is no refresh-token or account recovery flow.
- Review the migrations and database schema together before using an existing database, because migration history may not fully match the current ORM models.

For local development and portfolio demonstration, use sample data and a non-production database. Before any public deployment, review authorization, configuration and secrets, migrations, backups, logging, validation, and operational monitoring.
