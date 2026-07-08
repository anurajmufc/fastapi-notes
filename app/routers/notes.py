from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from schemas import (NoteCreate, NoteResponse, NoteUpdate)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import models
from database import get_db

from auth import CurrentUser

router = APIRouter()

# Route to create a note


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note, ["author"])
    return new_note


# Route to get all notes


@router.get("", name="notes", response_model=list[NoteResponse])
async def get_notes(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Note).where(models.Note.user_id == current_user.id).options(selectinload(models.Note.author)))
    notes = result.scalars().all()
    return list(notes)

# Route to get a specific note based on its id


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(current_user: CurrentUser, note_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Note).where(models.Note.user_id == current_user.id).options(selectinload(models.Note.author)).where(models.Note.id == note_id))
    note = result.scalars().first()
    if note:
        return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Note not found")

# Route to update a note(full)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note_full(note_id: int, current_user: CurrentUser, note_data: NoteCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check if note exists in db
    result = await db.execute(select(models.Note).options(
        selectinload(models.Note.author)).where(models.Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this note")

    # Replace the note
    note.title = note_data.title
    note.content = note_data.content

    await db.commit()
    await db.refresh(note, ["author"])
    return note

# Route to update a note(partial)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note_partial(note_id: int, current_user: CurrentUser, note_data: NoteUpdate, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check if note exists in db
    result = await db.execute(select(models.Note).options(selectinload(models.Note.author)).where(models.Note.id == note_id))
    note = result.scalars().first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this note")

    # Update the note
    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    await db.commit()
    await db.refresh(note)
    return note

# Route to delete a specific note based on its id


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Note).options(
        selectinload(models.Note.author)).where(models.Note.id == note_id))
    note = result.scalars().first()

    # Check if note exists
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this note")

    await db.delete(note)
    await db.commit()
