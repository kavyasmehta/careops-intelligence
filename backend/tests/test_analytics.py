def _make_client(client, intake_headers, member_id):
    return client.post(
        "/api/v1/clients",
        json={
            "first_name": "Analytics",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "member_id": member_id,
            "status": "active",
            "assigned_team_id": "Intake North",
        },
        headers=intake_headers,
    ).json()["data"]


def test_analytics_overview_shape(client, ops_manager_headers):
    response = client.get("/api/v1/analytics/overview", headers=ops_manager_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    for key in [
        "resolution_time_by_severity",
        "authorization_outcomes",
        "eligibility_outcomes",
        "top_failure_reasons",
        "team_workload",
        "alerts_created_trend",
    ]:
        assert key in data
    assert len(data["alerts_created_trend"]) == 12


def test_eligibility_outcomes_reflect_created_checks(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-ANALYTICS-1")
    client.post(
        "/api/v1/eligibility-checks",
        json={
            "client_id": created["id"],
            "payer": "Aetna",
            "check_date": "2026-01-01T00:00:00Z",
            "coverage_status": "failed",
            "failure_reason": "Member ID not found",
        },
        headers=intake_headers,
    )

    response = client.get("/api/v1/analytics/overview", headers=ops_manager_headers)
    outcomes = {row["label"]: row for row in response.json()["data"]["eligibility_outcomes"]}
    assert outcomes["failed"]["count"] == 1
    assert outcomes["failed"]["pct"] == 100.0

    reasons = {row["reason"]: row["count"] for row in response.json()["data"]["top_failure_reasons"]}
    assert reasons["Member ID not found"] == 1


def test_team_workload_reflects_client_assignment(client, ops_manager_headers, intake_headers):
    _make_client(client, intake_headers, "M-ANALYTICS-2")

    response = client.get("/api/v1/analytics/overview", headers=ops_manager_headers)
    teams = {row["team"]: row for row in response.json()["data"]["team_workload"]}
    assert teams["Intake North"]["client_count"] == 1


def test_export_clients_csv(client, ops_manager_headers, intake_headers):
    _make_client(client, intake_headers, "M-ANALYTICS-3")

    response = client.get("/api/v1/analytics/export/clients", headers=ops_manager_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    body = response.text
    assert "member_id" in body.splitlines()[0]
    assert "M-ANALYTICS-3" in body


def test_export_alerts_csv_respects_status_filter(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-ANALYTICS-4")
    client.post(
        "/api/v1/alerts",
        json={
            "client_id": created["id"],
            "alert_type": "eligibility_failed",
            "severity": "high",
            "explanation": "test",
            "recommended_action": "test",
        },
        headers=ops_manager_headers,
    )

    open_export = client.get("/api/v1/analytics/export/alerts?status=open", headers=ops_manager_headers)
    resolved_export = client.get("/api/v1/analytics/export/alerts?status=resolved", headers=ops_manager_headers)
    assert created["id"] in open_export.text
    assert created["id"] not in resolved_export.text
