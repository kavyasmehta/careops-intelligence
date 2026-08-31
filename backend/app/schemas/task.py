from datetime import date, datetime

from pydantic import BaseModel, computed_field

from app.models.task import TaskBase, TaskPriority, TaskStatus


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_employee_id: str | None = None
    due_date: date | None = None


class TaskRead(TaskBase):
    id: str
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return self.status != TaskStatus.COMPLETED and self.due_date < date.today()
