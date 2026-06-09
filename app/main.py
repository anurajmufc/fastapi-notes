from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from schemas import NoteCreate, NoteResponse
app = FastAPI()


@app.get("/")
def read_root():
    return "Welcome to my notes api"


fake_notes_db = {
    1: {"id": 1, "title": "Apple", "content": "fruit", "date_created": "June 7,2026"},
    2: {"id": 2, "title": "Banana", "content": "fruit", "date_created": "June 7,2026"},
    3: {"id": 3, "title": "Laptop", "content": "MacBook", "date_created": "June 7,2026"}
}


@app.get("/api/notes", response_model=list[NoteResponse])
def get_notes():
    return list(fake_notes_db.values())


@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, q: str | None = None):
    if note_id in fake_notes_db:
        return fake_notes_db[note_id]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Note not found")


@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def CreateNote(note: NoteCreate):
    new_id = max(fake_notes_db.keys()) + 1 if fake_notes_db else 1
    new_note = fake_notes_db[new_id] = {
        "id": new_id,
        "title": note.title,
        "content": note.content,
        "date_created": "June 7,2026"
    }
    return new_note
