from datetime import date
from enum import StrEnum

from pydantic import BaseModel


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    client_id: str | None = None
    assigned_employee_id: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date
    status: TaskStatus = TaskStatus.OPEN
