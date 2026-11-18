from fastapi import FastAPI
from backend.app.api.v1.endpoints import auth, incidents , users
from backend.models import models
from backend.database.database import engine

app = FastAPI(title="Disaster Triage Response API")

models.Base.metadata.create_all(bind=engine)

@app.get("/home", tags=["Home"])
def home():
    return {"message": "Welcome to the Disaster Triage Response API"}

app.include_router(incidents.router)
app.include_router(users.router)
app.include_router(auth.router)