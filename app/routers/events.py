from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=schemas.EventOut, status_code=201)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = crud.create_event(db, event)
    return crud.event_to_out(db, db_event)


@router.get("/", response_model=list[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    events = crud.get_events(db)
    return [crud.event_to_out(db, e) for e in events]


@router.get("/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.event_to_out(db, event)


@router.put("/{event_id}", response_model=schemas.EventOut)
def update_event(event_id: int, updates: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = crud.update_event(db, event_id, updates)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.event_to_out(db, event)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.delete_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return None


@router.get("/{event_id}/registrations", response_model=list[schemas.RegistrationOut])
def get_event_registrations(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.get_registrations_for_event(db, event_id)
