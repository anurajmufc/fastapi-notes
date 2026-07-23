# Job Application Tracker API

A RESTful Job Application Tracker API built using FastAPI and async SQLAlchemy, backed by PostgreSQL. Users can be created and managed, each user can own multiple job applications.

## Tech Stack

- **FastAPI** - async web framework
- **SQLAlchemy 2.0** - orm with asyncpg/AsyncSession
- **PostgreSQL** - relational database
- **Pydantic v2** - request/response validation and serialization
- **Pipenv** - dependency management
- **Alembic** - database migrations
- **argon2 + JWT** - password hashing and token-based authentication

## Features

- Full CRUD for job applications(create, read, update(full/partial), delete)
- User management with username/email
- JWT authentication with argon2 password hashing (all application routes require a logged-in user)
- One-to-many relationships (users -> job applications) with cascade delete
- Async, non-blocking database access
- Routes organized into modular APIRouters

## Getting started

- Python 3.13
- PostgreSQL running locally
- Pipenv
  
### 1. Create the database

```bash
sudo -u postgres psql
CREATE USER jobs_user WITH PASSWORD 'your_password';
CREATE DATABASE jobs_db OWNER jobs_user;
```

### 2. Configure Environment

Create .env file in the project root:

```bash
DB_URL=postgresql+asyncpg://jobs_user:your_password@localhost:5432/jobs_db
```

### 3. Install dependencies

```bash
pipenv install
```

### 4. Generate database

```bash
alembic upgrade head
```

### 5. Run the app

```bash
cd app
pipenv run uvicorn main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation.

## API Endpoints

|Method|Path|Description|
|------|------------|-----------|
|GET|/api/applications|List all job applications|
|POST|/api/applications|Create a job application|
|GET|/api/applications/{id}|Get a job application by ID|
|PUT|/api/applications/{id}|Fully replace a job application|
|PATCH|/api/applications/{id}|Partially update a job application|
|DELETE|/api/applications/{id}|Delete a job application|
|POST|/api/users/token|Returns a JWT access token|
|GET|/api/users/me|Get current user|
|POST|/api/users|Create a user|
|GET|/api/users/{id}|Get a user by ID|
|PATCH|/api/users/{id}|Partially update a user|
|DELETE|/api/users/{id}|Delete a user|

## Project Structure

```
app/
├── main.py          # App entry point, router registration, lifespan
├── database.py      # Async engine, session factory, Base
├── models.py        # SQLAlchemy ORM models (User, JobApplication)
├── schemas.py       # Pydantic schemas (validation & serialization)
├── auth.py          # Generate and verify JWTs, get current user
├── config.py        # Environment Configuration
└── routers/
    ├── applications.py     # /api/applications routes
    └── users.py            # /api/users routes
```

## Planned enhancements

- [ ] Soft deletes
- [ ] PostgreSQL full-text search
- [ ] Global exception handling
- [ ] Redis caching layer
- [ ] Celery background tasks
- [ ] Dockerization
- [ ] CI with Github actions and pytest