from typing import Annotated

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from schemas import NoteCreate, NoteResponse, UserCreate, UserResponse

from sqlalchemy import select

from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)


app = FastAPI()

# Home route
@app.get("/")
def read_root():
    return "Welcome to my notes api"

# Route to get all notes
@app.get("/api/notes", name="notes")
def get_notes(db: Annotated[Session, Depends(get_db)]):
    result=db.execute(select(models.Note))
    notes=result.scalars().all()
    return list(notes)

# Route to get a specific note based on its id
@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db:Annotated[Session,Depends(get_db)]):
    result=db.execute(select(models.Note).where(models.Note.id==note_id))
    note=result.scalars().first()
    if note:
        return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Note not found")

# Route to create user
@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(
        models.User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = db.execute(select(models.User).where(
        models.User.email == user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# route to find a specific user based on user id
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(
        models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found")

# Route to get all notes created by a user
@app.get("/api/users/{user_id}/notes", response_model=list[NoteResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(
        models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result=db.execute(select(models.Note).where(models.Note.user_id == user_id))
    notes=result.scalars().all()
    return notes


# Route to create a note
@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Annotated[Session,Depends(get_db)]):
    result=db.execute(select(models.User).where(models.User.id==note.user_id))
    user=result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found")
    new_note=models.Note(
        title=note.title,
        content=note.content,
        user_id=note.user_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note