from fastapi import APIRouter, Depends, Query

from app.core.errors import NotFoundError
from app.core.roles import Role, require_role
from app.db.mongo import get_database
from app.db.neo4j import get_neo4j_driver
from app.schemas.common import ItemResponse, ListResponse, PageMeta
from app.schemas.graph import (
    AppointmentWithoutAuthorization,
    ClientEgoNetwork,
    EmployeeRiskWorkload,
    PayerFailureRate,
    ProviderUnresolvedCases,
    SimilarClient,
)
from app.services import graph_insights

router = APIRouter(prefix="/api/v1/graph", tags=["graph"], dependencies=[Depends(require_role(*Role))])


def _wrap(data: list) -> ListResponse:
    return ListResponse(data=data, meta=PageMeta(page=1, page_size=len(data) or 1, total=len(data)))


@router.get("/insights/appointments-without-authorization", response_model=ListResponse[AppointmentWithoutAuthorization])
async def appointments_without_authorization(limit: int = Query(default=20, ge=1, le=100)):
    driver = get_neo4j_driver()
    data = await graph_insights.appointments_without_authorization(driver, limit=limit)
    return _wrap(data)


@router.get("/insights/providers-unresolved-authorizations", response_model=ListResponse[ProviderUnresolvedCases])
async def providers_unresolved_authorizations(limit: int = Query(default=10, ge=1, le=50)):
    driver = get_neo4j_driver()
    data = await graph_insights.providers_with_unresolved_authorizations(driver, limit=limit)
    return _wrap(data)


@router.get("/insights/payer-failure-rates", response_model=ListResponse[PayerFailureRate])
async def payer_failure_rates(limit: int = Query(default=10, ge=1, le=50)):
    driver = get_neo4j_driver()
    data = await graph_insights.payer_failure_rates(driver, get_database(), limit=limit)
    return _wrap(data)


@router.get("/insights/employee-risk-workload", response_model=ListResponse[EmployeeRiskWorkload])
async def employee_risk_workload(limit: int = Query(default=10, ge=1, le=50)):
    driver = get_neo4j_driver()
    data = await graph_insights.employee_risk_workload(driver, limit=limit)
    return _wrap(data)


@router.get("/insights/similar-clients/{client_id}", response_model=ListResponse[SimilarClient])
async def similar_clients(client_id: str, limit: int = Query(default=10, ge=1, le=50)):
    driver = get_neo4j_driver()
    data = await graph_insights.similar_clients(driver, client_id, limit=limit)
    return _wrap(data)


@router.get("/clients/{client_id}/ego", response_model=ItemResponse[ClientEgoNetwork])
async def client_ego_network(client_id: str):
    driver = get_neo4j_driver()
    network = await graph_insights.client_ego_network(driver, client_id)
    if not network.nodes:
        raise NotFoundError(f"No graph data found for client {client_id}")
    return ItemResponse(data=network)
