from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class TaskRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, client_id: str | None, status: str | None, assigned_employee_id: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if client_id:
            filter_["client_id"] = client_id
        if status:
            filter_["status"] = status
        if assigned_employee_id:
            filter_["assigned_employee_id"] = assigned_employee_id
        return filter_


def get_task_repository() -> TaskRepository:
    return TaskRepository(get_database()["tasks"])
