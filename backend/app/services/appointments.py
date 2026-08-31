from app.core.errors import NotFoundError
from app.db.mongo import get_database
from app.repositories.appointments import AppointmentRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.audit import record_audit


class AppointmentService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    async def list(self, *, client_id, status, provider, service_type, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(
            client_id=client_id, status=status, provider=provider, service_type=service_type
        )
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, appointment_id: str) -> dict:
        doc = await self.repository.get(appointment_id)
        if not doc:
            raise NotFoundError(f"Appointment {appointment_id} not found")
        return doc

    async def create(self, payload: AppointmentCreate, *, user: str) -> dict:
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(), user=user, action="create", entity_type="appointment",
            entity_id=doc["id"], new_value=doc,
        )
        return doc

    async def update(self, appointment_id: str, payload: AppointmentUpdate, *, user: str) -> dict:
        existing = await self.get(appointment_id)
        updated = await self.repository.update(appointment_id, payload.model_dump(mode="json", exclude_unset=True))
        if not updated:
            raise NotFoundError(f"Appointment {appointment_id} not found")
        await record_audit(
            get_database(), user=user, action="update", entity_type="appointment",
            entity_id=appointment_id, previous_value=existing, new_value=updated,
        )
        return updated
