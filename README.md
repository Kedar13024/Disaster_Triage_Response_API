# Disaster Triage Response API

A FastAPI backend for registering users and reporting and managing disaster incidents. The API stores users and incidents in PostgreSQL using SQLAlchemy, with Alembic migrations. Anyone can browse published incidents. Authenticated users can report incidents and manage their own reports; administrators can also manage incidents and look up user profiles.

> This is a learning and portfolio project. It is not a certified emergency dispatch or life-safety service.

## Features

- User registration with email, phone number, and password.
- Password hashing before credentials are stored.
- OAuth2 password-form login that returns a JWT bearer token.
- Incident updates and deletes are available to the reporter or an administrator.
- Administrator-only user profile lookup.
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

Published incident reads and user registration are public. Incident creation, the current user's incident list, updates, and deletes require a valid bearer token. Reporters and administrators can update or delete an incident; only administrators can look up user profiles. The public read endpoints ignore missing or invalid bearer credentials.

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/home` | None | Return a welcome message |
| `POST` | `/users` | None | Register a citizen account |
| `GET` | `/users/{user_id}` | Admin | Get a user's public profile |
| `POST` | `/login` | Form credentials | Verify credentials and return an access token |
| `GET` | `/incidents` | None | List published incidents; supports filters, pagination, and sorting |
| `GET` | `/incidents/{incident_id}` | None | Get a published incident; unpublished reports are visible to their owner or an admin |
| `GET` | `/incidents/my` | Bearer token | List incidents reported by the current user, including unpublished reports |
| `POST` | `/incidents` | Bearer token | Report an incident as the current user |
| `PATCH` | `/incidents/{incident_id}` | Bearer token | Update an incident reported by the current user or an admin |
| `DELETE` | `/incidents/{incident_id}` | Bearer token | Delete an incident reported by the current user or by an admin |

Use the slashless collection paths shown above (for example, `/incidents`). FastAPI redirects collection requests that include a trailing slash. The incident feed returns `200` with an empty array when no reports match. Incident detail returns `404` for an unknown ID and `403` when the caller cannot view an unpublished report. Updates return `400` for an empty update body, `404` for an unknown incident, and `403` when the caller is neither the reporter nor an admin.

The incident feed accepts these optional query parameters:

| Parameter | Values or format | Default |
| --- | --- | --- |
| `limit` | Integer from 1 to 100 | `20` |
| `skip` | Non-negative integer | `0` |
| `severity` | `low`, `medium`, `high`, `critical` | No filter |
| `incident_category` | One of the supported category values | No filter |
| `incident_type` | One of the supported incident type values | No filter |
| `start_date`, `end_date` | ISO datetime | No date bound |
| `search` | 1-200 characters; searches descriptions | No filter |
| `sort_by` | `newest`, `oldest`, `severity` | `newest` |

For example: `GET /incidents?severity=high&sort_by=newest&limit=10`.

## Authentication

Register an account with `POST /users` using JSON:

```json
{
  "user_fullname": "Alex Example",
  "user_phoneno": "+919876543210",
  "user_email": "alex@example.com",
  "user_password": "choose-a-strong-password"
}
```

New accounts receive the `citizen` role. Login at `POST /login` using form-encoded fields named `username` (the account email) and `password`. The response contains an access token and token type:

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

Newly registered accounts always receive the `citizen` role; the registration endpoint does not accept a requested role.

## Reporting an incident

Send `POST /incidents` with a bearer token and JSON body:

```json
{
  "incident_category": "natural_disaster",
  "incident_type": "flood",
  "description": "Rising water reported near the east bridge."
}
```

The API assigns the incident ID, report timestamp, reporter, default severity (`low`), and default published state (`true`). The response includes the reporter's public profile, including their email address. The create request accepts only the three fields shown; severity and publication state cannot be set through this endpoint.

## Tests

The tests use PostgreSQL and connect to a database named `dtr_db_test` using the database credentials in `.env`. Run them with:

```powershell
pytest
```

The test fixture creates and drops the tables in `dtr_db_test`. Use a disposable test database and do not point this setting at a database containing data you need to keep.

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

- Incident severity is stored as a string, and the API does not yet implement responder assignment or an incident status workflow.
- Public incident responses include the reporter profile, including email; review this exposure before deployment.
- Authentication uses bearer access tokens; there is no refresh-token or account recovery flow.
- Incident category and type are not checked as a pair, so they can describe inconsistent classifications.
- The `responder` role exists, but no endpoint currently grants it distinct permissions.

For local development and portfolio demonstration, use sample data and a non-production database. Before any public deployment, review authorization, configuration and secrets, migrations, backups, logging, validation, and operational monitoring.
