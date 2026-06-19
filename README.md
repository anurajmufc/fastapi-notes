# Notes API

A RESTful notes API built using FastAPI and async SQLAlchemy, backed by PostgreSQL. Users can be created and managed, each user can own multiple notes.

## Tech Stack

- **FastAPI** - async web framework
- **SQLAlchemy 2.0** - orm with asyncpg/AsyncSession
- **PostgreSQL** - relational database
- **Pydantic v2** - request/response validation and serialization
- **Pipenv** - dependency management

## Features

- Full CRUD for notes(create, read, update(full/partial), delete)
- User management with username/email
- One-to-many relationships (users -> notes) with cascade delete
- Async, non-blocking database access
- Routes organized into modular APIRouters

## Getting started

- Python 3.13
- PostgreSQL running locally
- -Pipenv
  
### 1. Create the database

```bash
sudo -u postgres psql
CREATE USER notes_user WITH PASSWORD 'your_password';
CREATE DATABASE notes_db OWNER notes_user;
```

### 2. Configure Environment

Create .env file in the project root:

```bash
DB_URL=postgresql+asyncpg://notes_user:your_password@localhost:5432/notes_db
```

### 3. Install dependencies

```bash
pipenv install
```

#### 4. Run the app

```bash
cd app
pipenv run uvicorn main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation.

## API Endpoints

|Method|Path|Description|
|------|------------|-----------|
|GET|/api/notes|List all notes|
|POST|/api/notes|Create a note|
|GET|/api/notes/{id}|Get a note by ID|
|PUT|/api/notes/{id}|Fully replace a note|
|PATCH|/api/notes/{id}|Partially update a note|
|DELETE|/api/notes/{id}|Delete a note|
|POST|/api/users|Create a user|
|GET|/api/users/{id}|Get a user by ID|
|PATCH|/api/users/{id}|Partially update a user|
|DELETE|/api/users/{id}|Delete a user|
|GET|/api/users/{id}/notes|List a user's notes|

## Project Structure

```
app/
├── main.py          # App entry point, router registration, lifespan
├── database.py      # Async engine, session factory, Base
├── models.py        # SQLAlchemy ORM models (User, Note)
├── schemas.py       # Pydantic schemas (validation & serialization)
└── routers/
    ├── notes.py     # /api/notes routes
    └── users.py     # /api/users routes
```

## Roadmap

I plan to upgrade this notes API into a full job application tracker  - a tool to manage job applications with user authentication and a frontend. These are some of the enhancements i would like to add in the future:

- [ ] Soft deletes
- [ ] PostgreSQL full-text search
- [ ] Global exception handling
- [ ] Redis caching layer
- [ ] Celery background tasks
- [ ] Dockerization
- [ ] CI with Github actions and pytest