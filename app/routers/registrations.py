from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/", response_model=schemas.RegistrationOut, status_code=201)
def register_for_event(
    reg: schemas.RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = crud.get_event(db, reg.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if crud.get_active_registration(db, current_user.id, reg.event_id):
        raise HTTPException(
            status_code=400,
            detail="You are already registered (or waitlisted) for this event",
        )

    return crud.create_registration(db, current_user.id, event)


@router.get("/{reg_id}", response_model=schemas.RegistrationOut)
def get_registration(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    reg = crud.get_registration(db, reg_id)
    if not reg or reg.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@router.delete("/{reg_id}", response_model=schemas.RegistrationOut)
def cancel_registration(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    reg = crud.get_registration(db, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if reg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own registration")

    cancelled = crud.cancel_registration(db, reg_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail="Registration is already cancelled")
    return cancelled