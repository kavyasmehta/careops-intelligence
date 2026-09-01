"""Graph endpoint tests.

Neo4j (unlike Mongo) has no per-test-database isolation in Community
Edition, so these tests can't assert exact counts against fixture data
the way the Mongo-backed tests do. Instead they assert: the endpoints
never error regardless of what's currently in the graph, response
shapes are correct, and the one hybrid endpoint (payer failure rates)
is fully deterministic because its Mongo half uses a payer name that
can't already exist in the graph.
"""
import uuid


def test_appointments_without_authorization_returns_well_formed_list(client, ops_manager_headers):
    response = client.get("/api/v1/graph/insights/appointments-without-authorization", headers=ops_manager_headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert body["meta"]["total"] == len(body["data"])


def test_providers_unresolved_authorizations_returns_well_formed_list(client, ops_manager_headers):
    response = client.get("/api/v1/graph/insights/providers-unresolved-authorizations", headers=ops_manager_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_employee_risk_workload_returns_well_formed_list(client, ops_manager_headers):
    response = client.get("/api/v1/graph/insights/employee-risk-workload", headers=ops_manager_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_similar_clients_for_unknown_client_is_empty_not_error(client, ops_manager_headers):
    fake_id = uuid.uuid4().hex
    response = client.get(f"/api/v1/graph/insights/similar-clients/{fake_id}", headers=ops_manager_headers)
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_ego_network_for_unknown_client_is_404(client, ops_manager_headers):
    fake_id = uuid.uuid4().hex
    response = client.get(f"/api/v1/graph/clients/{fake_id}/ego", headers=ops_manager_headers)
    assert response.status_code == 404


def test_payer_failure_rate_is_deterministic_for_a_payer_absent_from_the_graph(
    client, ops_manager_headers, intake_headers
):
    # A payer name guaranteed not to exist in the (shared, unisolated) Neo4j
    # graph, so total_covered_clients is deterministically 0 regardless of
    # what else is seeded there.
    unique_payer = f"TestPayer-{uuid.uuid4().hex[:8]}"

    created = client.post(
        "/api/v1/clients",
        json={
            "first_name": "Graph",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "member_id": f"M-{uuid.uuid4().hex[:8]}",
            "status": "active",
        },
        headers=intake_headers,
    ).json()["data"]

    client.post(
        "/api/v1/eligibility-checks",
        json={
            "client_id": created["id"],
            "payer": unique_payer,
            "check_date": "2026-01-01T00:00:00Z",
            "coverage_status": "failed",
            "failure_reason": "Member ID not found",
        },
        headers=intake_headers,
    )

    response = client.get("/api/v1/graph/insights/payer-failure-rates", headers=ops_manager_headers)
    assert response.status_code == 200
    rows = {row["payer"]: row for row in response.json()["data"]}
    assert unique_payer in rows
    row = rows[unique_payer]
    assert row["failed_checks"] == 1
    assert row["total_covered_clients"] == 0
    assert row["failure_rate"] == 0.0
