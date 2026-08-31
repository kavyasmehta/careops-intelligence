from datetime import date, timedelta
from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class AuthorizationRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, client_id: str | None, status: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if client_id:
            filter_["client_id"] = client_id
        if status:
            filter_["status"] = status
        return filter_

    async def find_expiring(self, within_days: int) -> list[dict]:
        cutoff = (date.today() + timedelta(days=within_days)).isoformat()
        today = date.today().isoformat()
        cursor = self.collection.find(
            {
                "status": {"$in": ["active", "pending"]},
                "expiration_date": {"$gte": today, "$lte": cutoff},
            }
        ).sort("expiration_date", 1)
        return [self.serialize(doc) async for doc in cursor]


def get_authorization_repository() -> AuthorizationRepository:
    return AuthorizationRepository(get_database()["authorizations"])
