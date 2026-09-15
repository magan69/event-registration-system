# Event Registration System — Backend API

A REST API that lets users register for events with limited capacity. Built with
**FastAPI**, **SQLAlchemy**, and **SQLite**.

Built for the ACM Web Team 2026–27 Backend assignment (Task 4: Event Registration System).

## Features

**Minimum requirements (from assignment brief):**
- Add and manage events (create, list, view, update, delete)
- Users can register for events
- Live tracking of registered participant count per event
- Registrations are automatically blocked once an event's capacity is reached
- All data (events, users, registrations) persisted in a database (SQLite)

**Bonus features implemented:**
- **Waitlist**: once an event is full, new registrations are automatically
  placed on a waitlist instead of being rejected outright.
- **Cancellation**: users can cancel a registration. If a *confirmed* spot
  opens up, the longest-waiting waitlisted user is automatically promoted.

## Tech Stack

- **Python 3.10+**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database (single file, zero setup)
- **Uvicorn** — ASGI server

## Project Structure

```
event-registration-system/
├── app/
│   ├── main.py              # FastAPI app + route registration
│   ├── database.py          # DB engine/session setup
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py               # Business logic (capacity checks, waitlist)
│   └── routers/
│       ├── users.py
│       ├── events.py
│       └── registrations.py
├── requirements.txt
└── README.md
```

## Setup & Run

1. **Clone the repo and enter the folder**
   ```bash
   git clone <your-repo-url>
   cd event-registration-system
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Open the interactive API docs**
   Go to **http://127.0.0.1:8000/docs** in your browser. This is auto-generated
   by FastAPI (Swagger UI) — you can test every endpoint directly from here,
   which is also perfect for taking your submission screenshots.

   A database file `event_registration.db` is created automatically on first run.

## API Endpoints

### Users
| Method | Endpoint          | Description        |
|--------|-------------------|---------------------|
| POST   | `/users/`         | Create a user       |
| GET    | `/users/`         | List all users      |
| GET    | `/users/{id}`     | Get a single user   |

### Events
| Method | Endpoint                      | Description                          |
|--------|-------------------------------|---------------------------------------|
| POST   | `/events/`                    | Create an event                       |
| GET    | `/events/`                    | List all events (with live counts)    |
| GET    | `/events/{id}`                | Get a single event                    |
| PUT    | `/events/{id}`                | Update an event                       |
| DELETE | `/events/{id}`                | Delete an event                       |
| GET    | `/events/{id}/registrations`  | List all registrations for an event   |

### Registrations
| Method | Endpoint               | Description                                              |
|--------|------------------------|------------------------------------------------------------|
| POST   | `/registrations/`      | Register a user for an event (confirmed or waitlisted)     |
| GET    | `/registrations/{id}`  | Get a single registration                                   |
| DELETE | `/registrations/{id}`  | Cancel a registration (may promote a waitlisted user)        |

## Example Usage

**1. Create a user**
```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Aditi Sharma", "email": "aditi@example.com"}'
```

**2. Create an event with capacity 2**
```bash
curl -X POST http://127.0.0.1:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Intro to Web Dev Workshop", "description": "Hands-on session", "location": "Lab 3", "date": "2026-09-20T10:00:00", "capacity": 2}'
```

**3. Register the user for the event**
```bash
curl -X POST http://127.0.0.1:8000/registrations/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "event_id": 1}'
```

**4. Register more users than capacity** → the 3rd registration for a
capacity-2 event automatically comes back with `"status": "waitlisted"`
instead of an error, and a 4th duplicate registration attempt for the same
user+event returns `400 Bad Request`.

**5. Cancel a confirmed registration** → the next waitlisted user for that
event is automatically promoted to `"confirmed"`.

## Design Notes

- **Capacity enforcement**: `crud.create_registration` counts existing
  `confirmed` registrations for an event and only confirms a new one if
  `confirmed_count < capacity`; otherwise the registration is created with
  `status="waitlisted"`. Capacity is never exceeded.
- **No duplicate registrations**: a user cannot hold two active (confirmed
  or waitlisted) registrations for the same event at once.
- **Waitlist promotion**: cancelling a confirmed registration triggers a
  check for the oldest waitlisted registration on that event, which is
  promoted to confirmed — keeping the event as full as possible without
  ever exceeding capacity.

## Author

Built for the ACM Student Chapter Web Team 2026–27, Backend Category —
Task 4: Event Registration System.
