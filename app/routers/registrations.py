from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/", response_model=schemas.RegistrationOut, status_code=201)
def register_for_event(reg: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db, reg.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    event = crud.get_event(db, reg.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if crud.get_active_registration(db, reg.user_id, reg.event_id):
        raise HTTPException(
            status_code=400,
            detail="User is already registered (or waitlisted) for this event",
        )

    return crud.create_registration(db, reg, event)


@router.get("/{reg_id}", response_model=schemas.RegistrationOut)
def get_registration(reg_id: int, db: Session = Depends(get_db)):
    reg = crud.get_registration(db, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@router.delete("/{reg_id}", response_model=schemas.RegistrationOut)
def cancel_registration(reg_id: int, db: Session = Depends(get_db)):
    reg = crud.cancel_registration(db, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found or already cancelled")
    return reg
