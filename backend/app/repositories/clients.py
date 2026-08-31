from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class ClientRepository(RepositoryBase):
    async def find_by_member_id(self, member_id: str) -> dict | None:
        doc = await self.collection.find_one({"member_id": member_id})
        return self.serialize(doc) if doc else None

    @staticmethod
    def build_filter(*, status: str | None, team_id: str | None, employee_id: str | None, q: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if status:
            filter_["status"] = status
        if team_id:
            filter_["assigned_team_id"] = team_id
        if employee_id:
            filter_["assigned_employee_id"] = employee_id
        if q:
            filter_["$text"] = {"$search": q}
        return filter_


def get_client_repository() -> ClientRepository:
    return ClientRepository(get_database()["clients"])
