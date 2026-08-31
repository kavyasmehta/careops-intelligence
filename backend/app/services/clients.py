from app.core.errors import ConflictError, NotFoundError
from app.db.mongo import get_database
from app.repositories.clients import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.audit import record_audit


class ClientService:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    async def list(self, *, status, team_id, employee_id, q, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(status=status, team_id=team_id, employee_id=employee_id, q=q)
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, client_id: str) -> dict:
        client = await self.repository.get(client_id)
        if not client:
            raise NotFoundError(f"Client {client_id} not found")
        return client

    async def create(self, payload: ClientCreate, *, user: str) -> dict:
        if await self.repository.find_by_member_id(payload.member_id):
            raise ConflictError(f"A client with member_id '{payload.member_id}' already exists")
        client = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(),
            user=user,
            action="create",
            entity_type="client",
            entity_id=client["id"],
            new_value=client,
        )
        return client

    async def update(self, client_id: str, payload: ClientUpdate, *, user: str) -> dict:
        existing = await self.get(client_id)
        changes = payload.model_dump(mode="json", exclude_unset=True)
        updated = await self.repository.update(client_id, changes)
        if not updated:
            raise NotFoundError(f"Client {client_id} not found")
        await record_audit(
            get_database(),
            user=user,
            action="update",
            entity_type="client",
            entity_id=client_id,
            previous_value=existing,
            new_value=updated,
        )
        return updated
