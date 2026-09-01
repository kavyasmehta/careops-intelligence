"""Service layer for the 5 required graph business insights plus the
client ego-network used by the Network Intelligence page.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from neo4j import AsyncDriver

from app.graph import cypher
from app.schemas.graph import (
    ClientEgoNetwork,
    EgoEdge,
    EgoNode,
)


async def _run(driver: AsyncDriver, query: str, **params) -> list[dict]:
    async with driver.session() as session:
        result = await session.run(query, **params)
        records = await result.data()
        return records


async def appointments_without_authorization(driver: AsyncDriver, limit: int = 20) -> list[dict]:
    return await _run(driver, cypher.APPOINTMENTS_WITHOUT_AUTHORIZATION, limit=limit)


async def providers_with_unresolved_authorizations(driver: AsyncDriver, limit: int = 10) -> list[dict]:
    return await _run(driver, cypher.PROVIDERS_WITH_UNRESOLVED_AUTHORIZATIONS, limit=limit)


async def payer_failure_rates(driver: AsyncDriver, db: AsyncIOMotorDatabase, limit: int = 10) -> list[dict]:
    """Hybrid: failure counts come from Mongo (source of truth for
    eligibility outcomes); total-covered-clients comes from the graph's
    CLIENT_COVERED_BY_PAYER edges. Combined into a real failure *rate*.
    """
    pipeline = [
        {"$match": {"coverage_status": "failed"}},
        {"$group": {"_id": "$payer", "failed_checks": {"$sum": 1}}},
    ]
    failed_by_payer = {doc["_id"]: doc["failed_checks"] async for doc in db["eligibility_checks"].aggregate(pipeline)}

    results = []
    for payer, failed_checks in failed_by_payer.items():
        rows = await _run(driver, cypher.PAYER_TOTAL_COVERED_CLIENTS, payer=payer)
        total_covered = rows[0]["total_covered"] if rows else 0
        failure_rate = round(100 * failed_checks / total_covered, 1) if total_covered else 0.0
        results.append(
            {
                "payer": payer,
                "failed_checks": failed_checks,
                "total_covered_clients": total_covered,
                "failure_rate": failure_rate,
            }
        )
    results.sort(key=lambda r: r["failed_checks"], reverse=True)
    return results[:limit]


async def employee_risk_workload(driver: AsyncDriver, limit: int = 10) -> list[dict]:
    return await _run(driver, cypher.EMPLOYEE_RISK_WORKLOAD, limit=limit)


async def similar_clients(driver: AsyncDriver, client_id: str, limit: int = 10) -> list[dict]:
    return await _run(driver, cypher.SIMILAR_CLIENTS_BY_RISK_FACTOR, client_id=client_id, limit=limit)


async def client_ego_network(driver: AsyncDriver, client_id: str) -> ClientEgoNetwork:
    core_rows = await _run(driver, cypher.EGO_CORE, client_id=client_id)
    appt_rows = await _run(driver, cypher.EGO_RECENT_APPOINTMENTS, client_id=client_id, limit=6)
    auth_rows = await _run(driver, cypher.EGO_RECENT_AUTHORIZATIONS, client_id=client_id, limit=6)

    nodes: dict[str, EgoNode] = {}
    edges: list[EgoEdge] = []

    if not core_rows or not core_rows[0].get("client_id"):
        return ClientEgoNetwork(nodes=[], edges=[])

    core = core_rows[0]
    client_node_id = f"client:{core['client_id']}"
    nodes[client_node_id] = EgoNode(id=client_node_id, label=core["client_name"], type="Client")

    if core.get("employee_id"):
        emp_node_id = f"employee:{core['employee_id']}"
        nodes[emp_node_id] = EgoNode(id=emp_node_id, label=core["employee_name"], type="Employee")
        edges.append(EgoEdge(source=client_node_id, target=emp_node_id, type="ASSIGNED_TO"))

    for payer_name in core.get("payers") or []:
        payer_node_id = f"payer:{payer_name}"
        nodes[payer_node_id] = EgoNode(id=payer_node_id, label=payer_name, type="Payer")
        edges.append(EgoEdge(source=client_node_id, target=payer_node_id, type="COVERED_BY"))

    for risk_name in core.get("risk_factors") or []:
        rf_node_id = f"risk:{risk_name}"
        nodes[rf_node_id] = EgoNode(id=rf_node_id, label=risk_name.replace("_", " "), type="RiskFactor")
        edges.append(EgoEdge(source=client_node_id, target=rf_node_id, type="HAS_RISK_FACTOR"))

    for row in appt_rows:
        appt_node_id = f"appointment:{row['appointment_id']}"
        nodes[appt_node_id] = EgoNode(id=appt_node_id, label=row["status"] or "appointment", type="Appointment")
        edges.append(EgoEdge(source=client_node_id, target=appt_node_id, type="HAS_APPOINTMENT"))
        if row.get("provider_name"):
            prov_node_id = f"provider:{row['provider_name']}"
            nodes[prov_node_id] = EgoNode(id=prov_node_id, label=row["provider_name"], type="Provider")
            edges.append(EgoEdge(source=appt_node_id, target=prov_node_id, type="WITH_PROVIDER"))

    for row in auth_rows:
        auth_node_id = f"authorization:{row['authorization_id']}"
        nodes[auth_node_id] = EgoNode(
            id=auth_node_id, label=row["authorization_number"], type="Authorization"
        )
        edges.append(EgoEdge(source=client_node_id, target=auth_node_id, type="HAS_AUTHORIZATION"))
        if row.get("service_name"):
            svc_node_id = f"service:{row['service_name']}"
            nodes[svc_node_id] = EgoNode(id=svc_node_id, label=row["service_name"], type="Service")
            edges.append(EgoEdge(source=auth_node_id, target=svc_node_id, type="FOR_SERVICE"))

    return ClientEgoNetwork(nodes=list(nodes.values()), edges=edges)
