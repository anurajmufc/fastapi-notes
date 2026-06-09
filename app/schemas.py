from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_created: str
