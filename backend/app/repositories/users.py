from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class UserRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, role: str | None, team_id: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if role:
            filter_["role"] = role
        if team_id:
            filter_["team_id"] = team_id
        return filter_


def get_user_repository() -> UserRepository:
    return UserRepository(get_database()["users"])
