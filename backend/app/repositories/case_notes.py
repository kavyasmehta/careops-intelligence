from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class CaseNoteRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, client_id: str | None) -> dict[str, Any]:
        return {"client_id": client_id} if client_id else {}


def get_case_note_repository() -> CaseNoteRepository:
    return CaseNoteRepository(get_database()["case_notes"])
