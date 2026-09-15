from fastapi import FastAPI

from . import models
from .database import engine
from .routers import users, events, registrations

# Creates event_registration.db and all tables the first time this runs.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Registration System",
    description=(
        "Backend API for managing events, users, and registrations. "
        "Enforces event capacity and automatically waitlists users when an "
        "event is full."
    ),
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(events.router)
app.include_router(registrations.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Event Registration System API is running.",
        "docs": "/docs",
    }
