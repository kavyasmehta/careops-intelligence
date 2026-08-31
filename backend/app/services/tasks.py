from datetime import UTC, datetime

from app.core.errors import NotFoundError
from app.db.mongo import get_database
from app.models.task import TaskStatus
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.audit import record_audit


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def list(self, *, client_id, status, assigned_employee_id, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(client_id=client_id, status=status, assigned_employee_id=assigned_employee_id)
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, task_id: str) -> dict:
        doc = await self.repository.get(task_id)
        if not doc:
            raise NotFoundError(f"Task {task_id} not found")
        return doc

    async def create(self, payload: TaskCreate, *, user: str) -> dict:
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(get_database(), user=user, action="create", entity_type="task", entity_id=doc["id"], new_value=doc)
        return doc

    async def update(self, task_id: str, payload: TaskUpdate, *, user: str) -> dict:
        existing = await self.get(task_id)
        changes = payload.model_dump(mode="json", exclude_unset=True)
        if changes.get("status") == TaskStatus.COMPLETED.value and existing["status"] != TaskStatus.COMPLETED.value:
            changes["completed_at"] = datetime.now(UTC).isoformat()
        updated = await self.repository.update(task_id, changes)
        if not updated:
            raise NotFoundError(f"Task {task_id} not found")
        await record_audit(
            get_database(), user=user, action="update", entity_type="task",
            entity_id=task_id, previous_value=existing, new_value=updated,
        )
        return updated
