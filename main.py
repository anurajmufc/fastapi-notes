from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return "Welcome to my notes api"


fake_notes_db = {
    1: {"id": 1, "title": "Apple", "content": "fruit"},
    2: {"id": 2, "title": "Banana", "content": "fruit"},
    3: {"id": 3, "title": "Laptop", "content": "MacBook"}
}


@app.get("/api/notes")
def get_notes():
    return fake_notes_db


@app.get("/api/notes/{note_id}")
def get_note(note_id: int, q: str | None = None):
    if note_id in fake_notes_db:
        return fake_notes_db[note_id]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Note not found")

 