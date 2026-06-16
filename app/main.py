from typing import Annotated

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from schemas import NoteCreate, NoteResponse, UserCreate, UserResponse, NoteUpdate, UserUpdate

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
    result = db.execute(select(models.Note))
    notes = result.scalars().all()
    return list(notes)

# Route to get a specific note based on its id


@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Note).where(models.Note.id == note_id))
    note = result.scalars().first()
    if note:
        return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Note not found")

# Route to update a note(full)


@app.put("/api/notes/{note_id}", response_model=NoteResponse)
def update_note_full(note_id: int, note_data: NoteCreate, db: Annotated[Session, Depends(get_db)]):

    # Check if note exists in db
    result = db.execute(select(models.Note).where(models.Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    # Check if user id linked to the note that is supposed to be changed exists
    if note_data.user_id != note.user_id:
        result = db.execute(select(models.User).where(
            models.User.id == note_data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

    # Replace the note
    note.title = note_data.title
    note.content = note_data.content
    note.user_id=note.user_id

    db.commit()
    db.refresh(note)
    return note

# Route to update a note(partial)


@app.patch("/api/notes/{note_id}", response_model=NoteResponse)
def update_note_partial(note_id: int, note_data: NoteUpdate, db: Annotated[Session, Depends(get_db)]):

    # Check if note exists in db
    result = db.execute(select(models.Note).where(models.Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    # Update the note
    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note

# Route to delete a specific note based on its id


@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Note).where(models.Note.id == note_id))
    note = result.scalars().first()

    # Check if note exists
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    db.delete(note)
    db.commit()


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


# Route to update user information(partial)


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Annotated[Session, Depends(get_db)]):

    # Check if user exists
    result = db.execute(select(models.User).where(
        models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if new username is different and it doesn't exist in the database already
    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(select(models.User).where(
            models.User.username == user_update.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    # Check if new username is different and it doesn't exist in the database already
    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(select(models.User).where(
            models.User.email == user_update.email))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Route to delete a user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    # Check if user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    db.delete(user)
    db.commit()

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = db.execute(select(models.Note).where(
        models.Note.user_id == user_id))
    notes = result.scalars().all()
    return notes


# Route to create a note
@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(
        models.User.id == note.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    new_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=note.user_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note
