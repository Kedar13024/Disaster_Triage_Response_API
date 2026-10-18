# Disaster Triage Response API

A beginner-friendly FastAPI project for reporting and managing disaster incidents. Incident data is stored in memory and resets whenever the server restarts.

## Run the API

From the project directory, activate the virtual environment and start the server:

```powershell
.venv\Scripts\Activate.ps1
fastapi dev backend/main.py
```

Open <http://127.0.0.1:8000/docs> to try the endpoints in the interactive API documentation.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/home` | Show a welcome message |
| GET | `/incidents` | List all incidents |
| GET | `/incidents/{incident_id}` | Get one incident by ID |
| POST | `/incidents` | Create an incident and assign its ID |
| PUT | `/incidents/{incident_id}` | Replace an incident's details |
| DELETE | `/incidents/{incident_id}` | Delete an incident |

## Incident fields

Each incident has these fields:

- `incident_id`: integer assigned by the API when creating an incident
- `incident_type`: string, such as `Flood` or `Wildfire`
- `incident_des`: short description of the incident
- `reported_at`: date and time in ISO 8601 format

For `POST /incidents` and `PUT /incidents/{incident_id}`, send JSON without `incident_id`, for example:

```json
{
  "incident_type": "Flood",
  "incident_des": "Rising water reported near the east bridge.",
  "reported_at": "2026-10-18T08:15:00"
}
```

If an incident ID does not exist, the API returns a `404` response.
