from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class EligibilityRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, client_id: str | None, coverage_status: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if client_id:
            filter_["client_id"] = client_id
        if coverage_status:
            filter_["coverage_status"] = coverage_status
        return filter_


def get_eligibility_repository() -> EligibilityRepository:
    return EligibilityRepository(get_database()["eligibility_checks"])
