from datetime import date

from fastapi import APIRouter, Depends

from app.core.roles import Role, require_role
from app.db.mongo import get_database
from app.schemas.common import ItemResponse
from app.schemas.dashboard import DashboardMetrics
from app.services.dashboard import compute_metrics

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=ItemResponse[DashboardMetrics], dependencies=[Depends(require_role(*Role))])
async def get_dashboard_metrics(
    team_id: str | None = None,
    payer: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    metrics = await compute_metrics(
        get_database(), team_id=team_id, payer=payer, status=status, date_from=date_from, date_to=date_to
    )
    return ItemResponse(data=metrics)
