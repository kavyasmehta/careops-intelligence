from datetime import datetime

from app.models.case_note import CaseNoteBase


class CaseNoteCreate(CaseNoteBase):
    pass


class CaseNoteRead(CaseNoteBase):
    id: str
    created_at: datetime
    updated_at: datetime
