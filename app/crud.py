from sqlalchemy.orm import Session

from . import models, schemas


# ============ Users ============
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


# ============ Events ============
def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event(db: Session, event_id: int) -> models.Event | None:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(db: Session) -> list[models.Event]:
    return db.query(models.Event).all()


def update_event(db: Session, event_id: int, updates: schemas.EventUpdate) -> models.Event | None:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_event, field, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> models.Event | None:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    db.delete(db_event)
    db.commit()
    return db_event


def get_confirmed_count(db: Session, event_id: int) -> int:
    return (
        db.query(models.Registration)
        .filter(
            models.Registration.event_id == event_id,
            models.Registration.status == models.RegistrationStatus.confirmed,
        )
        .count()
    )


def get_waitlisted_count(db: Session, event_id: int) -> int:
    return (
        db.query(models.Registration)
        .filter(
            models.Registration.event_id == event_id,
            models.Registration.status == models.RegistrationStatus.waitlisted,
        )
        .count()
    )


def event_to_out(db: Session, event: models.Event) -> dict:
    """Builds the API response for an event, including live registration counts."""
    confirmed = get_confirmed_count(db, event.id)
    waitlisted = get_waitlisted_count(db, event.id)
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "date": event.date,
        "capacity": event.capacity,
        "confirmed_count": confirmed,
        "waitlisted_count": waitlisted,
        "spots_left": max(event.capacity - confirmed, 0),
    }


# ============ Registrations ============
def get_active_registration(db: Session, user_id: int, event_id: int) -> models.Registration | None:
    """An 'active' registration is confirmed or waitlisted (not cancelled)."""
    return (
        db.query(models.Registration)
        .filter(
            models.Registration.user_id == user_id,
            models.Registration.event_id == event_id,
            models.Registration.status != models.RegistrationStatus.cancelled,
        )
        .first()
    )


def create_registration(db: Session, reg: schemas.RegistrationCreate, event: models.Event) -> models.Registration:
    """Confirms the registration if capacity allows, otherwise waitlists it.

    This is the core rule of the assignment: capacity is never exceeded.
    """
    confirmed_count = get_confirmed_count(db, reg.event_id)
    status = (
        models.RegistrationStatus.confirmed
        if confirmed_count < event.capacity
        else models.RegistrationStatus.waitlisted
    )
    db_reg = models.Registration(user_id=reg.user_id, event_id=reg.event_id, status=status)
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)
    return db_reg


def get_registration(db: Session, reg_id: int) -> models.Registration | None:
    return db.query(models.Registration).filter(models.Registration.id == reg_id).first()


def get_registrations_for_event(db: Session, event_id: int) -> list[models.Registration]:
    return db.query(models.Registration).filter(models.Registration.event_id == event_id).all()


def cancel_registration(db: Session, reg_id: int) -> models.Registration | None:
    """Cancels a registration. If it freed up a confirmed slot, promotes the
    longest-waiting waitlisted registration into that slot (bonus feature).
    """
    reg = get_registration(db, reg_id)
    if not reg or reg.status == models.RegistrationStatus.cancelled:
        return None

    was_confirmed = reg.status == models.RegistrationStatus.confirmed
    reg.status = models.RegistrationStatus.cancelled
    db.commit()

    if was_confirmed:
        next_in_line = (
            db.query(models.Registration)
            .filter(
                models.Registration.event_id == reg.event_id,
                models.Registration.status == models.RegistrationStatus.waitlisted,
            )
            .order_by(models.Registration.registered_at.asc())
            .first()
        )
        if next_in_line:
            next_in_line.status = models.RegistrationStatus.confirmed
            db.commit()

    db.refresh(reg)
    return reg
