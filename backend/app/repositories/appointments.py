from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class AppointmentRepository(RepositoryBase):
    @staticmethod
    def build_filter(
        *, client_id: str | None, status: str | None, provider: str | None, service_type: str | None
    ) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if client_id:
            filter_["client_id"] = client_id
        if status:
            filter_["status"] = status
        if provider:
            filter_["provider"] = provider
        if service_type:
            filter_["service_type"] = service_type
        return filter_


def get_appointment_repository() -> AppointmentRepository:
    return AppointmentRepository(get_database()["appointments"])
