from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.roles import Role, require_role
from app.db.mongo import get_database
from app.models.alert import AlertSeverity, AlertStatus
from app.models.appointment import AppointmentStatus
from app.models.authorization import AuthorizationStatus
from app.models.client import ClientStatus
from app.models.eligibility import CoverageStatus
from app.repositories.alerts import get_alert_repository
from app.repositories.appointments import get_appointment_repository
from app.repositories.authorizations import get_authorization_repository
from app.repositories.clients import get_client_repository
from app.repositories.eligibility import get_eligibility_repository
from app.schemas.analytics import AnalyticsOverview
from app.schemas.common import ItemResponse
from app.services.analytics import compute_overview
from app.services.csv_export import rows_to_csv

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"], dependencies=[Depends(require_role(*Role))])


@router.get("/overview", response_model=ItemResponse[AnalyticsOverview])
async def analytics_overview():
    overview = await compute_overview(get_database())
    return ItemResponse(data=overview)


def _csv_response(csv_text: str, filename: str) -> PlainTextResponse:
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/clients")
async def export_clients(status: ClientStatus | None = None, team_id: str | None = None):
    repo = get_client_repository()
    filter_ = repo.build_filter(status=status, team_id=team_id, employee_id=None, q=None)
    docs, _ = await repo.list(filter_, page=1, page_size=100_000)
    columns = [
        "id", "first_name", "last_name", "date_of_birth", "member_id", "email", "phone",
        "address", "assigned_team_id", "assigned_employee_id", "status", "created_at",
    ]
    return _csv_response(rows_to_csv(docs, columns), "clients.csv")


@router.get("/export/eligibility-checks")
async def export_eligibility_checks(coverage_status: CoverageStatus | None = None, client_id: str | None = None):
    repo = get_eligibility_repository()
    filter_ = repo.build_filter(client_id=client_id, coverage_status=coverage_status)
    docs, _ = await repo.list(filter_, page=1, page_size=100_000)
    columns = [
        "id", "client_id", "payer", "check_date", "coverage_status", "plan_name",
        "failure_reason", "source", "created_at",
    ]
    return _csv_response(rows_to_csv(docs, columns), "eligibility_checks.csv")


@router.get("/export/authorizations")
async def export_authorizations(status: AuthorizationStatus | None = None, client_id: str | None = None):
    repo = get_authorization_repository()
    filter_ = repo.build_filter(client_id=client_id, status=status)
    docs, _ = await repo.list(filter_, page=1, page_size=100_000)
    columns = [
        "id", "client_id", "payer", "authorization_number", "service_type",
        "units_approved", "units_used", "effective_date", "expiration_date", "status", "created_at",
    ]
    return _csv_response(rows_to_csv(docs, columns), "authorizations.csv")


@router.get("/export/appointments")
async def export_appointments(status: AppointmentStatus | None = None, client_id: str | None = None):
    repo = get_appointment_repository()
    filter_ = repo.build_filter(client_id=client_id, status=status, provider=None, service_type=None)
    docs, _ = await repo.list(filter_, page=1, page_size=100_000)
    columns = [
        "id", "client_id", "appointment_datetime", "service_type", "provider",
        "location", "status", "authorization_id", "created_at",
    ]
    return _csv_response(rows_to_csv(docs, columns), "appointments.csv")


@router.get("/export/alerts")
async def export_alerts(status: AlertStatus | None = None, severity: AlertSeverity | None = None, client_id: str | None = None):
    repo = get_alert_repository()
    filter_ = repo.build_filter(client_id=client_id, status=status, severity=severity, assigned_employee_id=None)
    docs, _ = await repo.list(filter_, page=1, page_size=100_000)
    columns = [
        "id", "client_id", "alert_type", "severity", "explanation", "recommended_action",
        "assigned_employee_id", "status", "resolution_notes", "resolved_at", "created_at",
    ]
    return _csv_response(rows_to_csv(docs, columns), "alerts.csv")
