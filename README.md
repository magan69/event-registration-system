# Event Registration System: Backend API

A REST API for a college event platform. Users can sign up, log in, and register for events that have limited capacity. When an event is full, new registrations go to a waitlist automatically, and when someone cancels, the longest-waiting person on the waitlist is confirmed.

Built by Magan shandilya as a Backend project for the TechSpace Tech Team recruitment. This is a backend-only project, so there is no UI. The API is tested through the auto-generated Swagger docs.

## Features

- Sign up and log in with **hashed passwords** (bcrypt) and **JWT** authentication
- Full CRUD for events, each with a capacity limit
- Register for an event and cancel a registration
- **Capacity is never exceeded**: when an event is full, the registration is set to `waitlisted`
- **Waitlist promotion**: cancelling a confirmed registration promotes the earliest waitlisted user
- **No duplicate registrations**: a user cannot hold two active registrations for the same event
- A user can only view or cancel **their own** registrations
- Input validation (Pydantic) and proper error responses (400, 401, 403, 404)
- Interactive API docs with Swagger UI at `/docs`

## Tech Stack

- Python
- FastAPI (web framework)
- SQLAlchemy (ORM) with SQLite (database)
- Pydantic (validation)
- bcrypt (password hashing) and PyJWT (tokens)
- python-dotenv (environment variables)
- Uvicorn (server)

## Project Structure

```
event-registration-system/
├── app/
│   ├── main.py            # app entry point
│   ├── database.py        # database connection
│   ├── models.py          # database tables
│   ├── schemas.py         # request/response validation
│   ├── crud.py            # business logic (capacity, waitlist)
│   ├── security.py        # password hashing and JWT creation
│   ├── deps.py            # get_current_user (token check)
│   └── routers/
│       ├── auth.py
│       ├── users.py
│       ├── events.py
│       └── registrations.py
├── screenshot/            # API screenshots
├── requirements.txt
├── .env.example
└── README.md
```

## How to Run

1. Clone the repo and open the folder:
   ```
   git clone https://github.com/magan69/event-registration-system.git
   cd event-registration-system
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Mac / Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create your `.env` file. Copy `.env.example` to `.env`, then replace the value with your own random key:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Your `.env` should look like this:
   ```
   SECRET_KEY=your_generated_key_here
   ```
5. Start the server:
   ```
   uvicorn app.main:app --reload
   ```
6. Open the API docs at **http://127.0.0.1:8000/docs**. The SQLite database file is created automatically on first run.

## Using the API

1. `POST /auth/signup` to create an account.
2. `POST /auth/login` to get an access token. In Swagger, click **Authorize** (top right), enter your email as `username` and your password, and every protected request will then send the token for you.
3. `POST /events/` to create an event with a `capacity`.
4. `POST /registrations/` with `{"event_id": 1}` to register. The response status is `confirmed` or `waitlisted`.

## API Endpoints

A lock means a valid token is required.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/signup` | Create an account | No |
| POST | `/auth/login` | Log in and get a JWT | No |
| GET | `/users/` | List users | No |
| GET | `/users/{user_id}` | Get one user | No |
| POST | `/events/` | Create an event | Yes |
| GET | `/events/` | List events with live counts | No |
| GET | `/events/{event_id}` | Get one event | No |
| PUT | `/events/{event_id}` | Update an event | Yes |
| DELETE | `/events/{event_id}` | Delete an event | Yes |
| GET | `/events/{event_id}/registrations` | List registrations of an event | No |
| POST | `/registrations/` | Register for an event (confirmed or waitlisted) | Yes |
| GET | `/registrations/{reg_id}` | Get your own registration | Yes |
| DELETE | `/registrations/{reg_id}` | Cancel your registration (may promote the waitlist) | Yes |

## Error Responses

| Code | Meaning |
|---|---|
| 400 | Bad request (e.g. duplicate email, already registered) |
| 401 | Missing, invalid or expired token, or wrong login details |
| 403 | Trying to cancel someone else's registration |
| 404 | User, event or registration not found |
| 422 | Invalid input (e.g. bad email format, capacity of 0) |

## Screenshots

API screenshots are in the `screenshot/` folder.

## Known Limitations

- Any logged-in user can create, update or delete events. Admin and student roles would be the next step.
- If two users take the last spot at exactly the same moment, a race condition is possible. A production version would use a database transaction with row locking.
- SQLite is used for simplicity. A larger deployment would use PostgreSQL.