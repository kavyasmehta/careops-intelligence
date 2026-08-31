from app.db.mongo import get_database
from app.repositories.case_notes import CaseNoteRepository
from app.schemas.case_note import CaseNoteCreate
from app.services.audit import record_audit


class CaseNoteService:
    def __init__(self, repository: CaseNoteRepository):
        self.repository = repository

    async def list(self, *, client_id, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(client_id=client_id)
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def create(self, payload: CaseNoteCreate, *, user: str) -> dict:
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(), user=user, action="create", entity_type="case_note", entity_id=doc["id"], new_value=doc
        )
        return doc
