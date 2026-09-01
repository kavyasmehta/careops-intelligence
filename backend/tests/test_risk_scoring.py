from datetime import date, timedelta


def _make_client(client, intake_headers, member_id):
    return client.post(
        "/api/v1/clients",
        json={
            "first_name": "Risk",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "member_id": member_id,
            "status": "active",
        },
        headers=intake_headers,
    ).json()["data"]


def test_risk_score_is_zero_with_no_conditions(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-RISK-1")
    response = client.get(f"/api/v1/clients/{created['id']}/risk", headers=ops_manager_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["score"] == 0
    assert data["band"] == "Low"
    assert data["factors"] == []


def test_risk_score_returns_404_for_unknown_client(client, ops_manager_headers):
    response = client.get("/api/v1/clients/64b64c1f2f3a4b5c6d7e8f90/risk", headers=ops_manager_headers)
    assert response.status_code == 404


def test_failed_eligibility_check_contributes_to_score(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-RISK-2")
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

    response = client.get(f"/api/v1/clients/{created['id']}/risk", headers=ops_manager_headers)
    data = response.json()["data"]
    codes = {f["code"] for f in data["factors"]}
    assert "eligibility_failed" in codes
    assert data["score"] == 20
    assert data["band"] == "Low"


def test_multiple_factors_combine_and_band_escalates(client, ops_manager_headers, intake_headers, auth_specialist_headers):
    created = _make_client(client, intake_headers, "M-RISK-3")

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
    client.post(
        "/api/v1/authorizations",
        json={
            "client_id": created["id"],
            "payer": "Aetna",
            "authorization_number": "AUTH-RISK-1",
            "service_type": "Physical Therapy",
            "units_approved": 10,
            "units_used": 10,
            "effective_date": str(date.today() - timedelta(days=30)),
            "expiration_date": str(date.today() + timedelta(days=60)),
            "status": "exhausted",
        },
        headers=auth_specialist_headers,
    )

    response = client.get(f"/api/v1/clients/{created['id']}/risk", headers=ops_manager_headers)
    data = response.json()["data"]
    codes = {f["code"] for f in data["factors"]}
    assert codes == {"eligibility_failed", "authorization_units_exhausted"}
    assert data["score"] == 35  # 20 + 15
    assert data["band"] == "Medium"


def test_overdue_task_contributes_to_score(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-RISK-4")
    client.post(
        "/api/v1/tasks",
        json={
            "title": "Follow up",
            "client_id": created["id"],
            "assigned_employee_id": "64b64c1f2f3a4b5c6d7e8f91",
            "priority": "high",
            "due_date": "2020-01-01",
        },
        headers=ops_manager_headers,
    )

    response = client.get(f"/api/v1/clients/{created['id']}/risk", headers=ops_manager_headers)
    data = response.json()["data"]
    codes = {f["code"] for f in data["factors"]}
    assert "overdue_task" in codes
    assert data["score"] == 15
