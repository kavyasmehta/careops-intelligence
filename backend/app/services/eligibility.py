from app.core.errors import NotFoundError
from app.db.mongo import get_database
from app.repositories.eligibility import EligibilityRepository
from app.schemas.eligibility import EligibilityCheckCreate, EligibilityCheckUpdate
from app.services.audit import record_audit


class EligibilityService:
    def __init__(self, repository: EligibilityRepository):
        self.repository = repository

    async def list(self, *, client_id, coverage_status, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(client_id=client_id, coverage_status=coverage_status)
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, check_id: str) -> dict:
        doc = await self.repository.get(check_id)
        if not doc:
            raise NotFoundError(f"Eligibility check {check_id} not found")
        return doc

    async def create(self, payload: EligibilityCheckCreate, *, user: str) -> dict:
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(), user=user, action="create", entity_type="eligibility_check",
            entity_id=doc["id"], new_value=doc,
        )
        return doc

    async def update(self, check_id: str, payload: EligibilityCheckUpdate, *, user: str) -> dict:
        existing = await self.get(check_id)
        updated = await self.repository.update(check_id, payload.model_dump(mode="json", exclude_unset=True))
        if not updated:
            raise NotFoundError(f"Eligibility check {check_id} not found")
        await record_audit(
            get_database(), user=user, action="update", entity_type="eligibility_check",
            entity_id=check_id, previous_value=existing, new_value=updated,
        )
        return updated
