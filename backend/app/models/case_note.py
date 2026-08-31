from pydantic import BaseModel, Field


class CaseNoteBase(BaseModel):
    client_id: str
    author: str
    note_text: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
