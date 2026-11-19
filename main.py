"""Application entry point for the Disaster Triage Response API."""

from fastapi import FastAPI
from backend.app.api.v1.endpoints import auth, incidents , users

app = FastAPI(title="Disaster Triage Response API")


@app.get("/home", tags=["Home"])
def home():
    """Return a welcome message from the service root endpoint."""
    return {"message": "Welcome to the Disaster Triage Response API"}

app.include_router(incidents.router)
app.include_router(users.router)
app.include_router(auth.router)
