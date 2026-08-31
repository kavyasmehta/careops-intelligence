from app.core.errors import NotFoundError
from app.db.mongo import get_database
from app.repositories.authorizations import AuthorizationRepository
from app.schemas.authorization import AuthorizationCreate, AuthorizationUpdate
from app.services.audit import record_audit


class AuthorizationService:
    def __init__(self, repository: AuthorizationRepository):
        self.repository = repository

    async def expiring(self, within_days: int) -> list[dict]:
        return await self.repository.find_expiring(within_days)

    async def list(self, *, client_id, status, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(client_id=client_id, status=status)
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, authorization_id: str) -> dict:
        doc = await self.repository.get(authorization_id)
        if not doc:
            raise NotFoundError(f"Authorization {authorization_id} not found")
        return doc

    async def create(self, payload: AuthorizationCreate, *, user: str) -> dict:
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(), user=user, action="create", entity_type="authorization",
            entity_id=doc["id"], new_value=doc,
        )
        return doc

    async def update(self, authorization_id: str, payload: AuthorizationUpdate, *, user: str) -> dict:
        existing = await self.get(authorization_id)
        updated = await self.repository.update(authorization_id, payload.model_dump(mode="json", exclude_unset=True))
        if not updated:
            raise NotFoundError(f"Authorization {authorization_id} not found")
        await record_audit(
            get_database(), user=user, action="update", entity_type="authorization",
            entity_id=authorization_id, previous_value=existing, new_value=updated,
        )
        return updated
