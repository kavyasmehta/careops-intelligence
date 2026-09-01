from datetime import date, timedelta


def _make_client(client, intake_headers, member_id, status="active", team_id="Intake North"):
    return client.post(
        "/api/v1/clients",
        json={
            "first_name": "Test",
            "last_name": "Client",
            "date_of_birth": "1990-01-01",
            "member_id": member_id,
            "status": status,
            "assigned_team_id": team_id,
        },
        headers=intake_headers,
    ).json()["data"]


def test_dashboard_metrics_shape(client, ops_manager_headers, intake_headers):
    _make_client(client, intake_headers, "M-DASH-1")
    _make_client(client, intake_headers, "M-DASH-2", status="pending")

    response = client.get("/api/v1/dashboard/metrics", headers=ops_manager_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["active_clients"] == 1
    assert data["eligibility_success_rate"] == 0.0
    assert any(row["label"] == "pending" and row["count"] == 1 for row in data["cases_by_status"])
    assert any(row["label"] == "active" and row["count"] == 1 for row in data["cases_by_status"])
    assert isinstance(data["eligibility_trend"], list)
    assert isinstance(data["workload_by_employee"], list)


def test_dashboard_status_filter_overrides_active_count(client, ops_manager_headers, intake_headers):
    _make_client(client, intake_headers, "M-DASH-3", status="pending")

    response = client.get("/api/v1/dashboard/metrics?status=pending", headers=ops_manager_headers)
    assert response.json()["data"]["active_clients"] == 1


def test_dashboard_team_filter_scopes_clients(client, ops_manager_headers, intake_headers):
    _make_client(client, intake_headers, "M-DASH-4", team_id="Intake North")
    _make_client(client, intake_headers, "M-DASH-5", team_id="Intake South")

    response = client.get("/api/v1/dashboard/metrics?team_id=Intake North", headers=ops_manager_headers)
    assert response.json()["data"]["active_clients"] == 1


def test_expiring_authorizations_included_in_metrics(client, ops_manager_headers, intake_headers, auth_specialist_headers):
    created_client = _make_client(client, intake_headers, "M-DASH-6")
    client.post(
        "/api/v1/authorizations",
        json={
            "client_id": created_client["id"],
            "payer": "Aetna",
            "authorization_number": "AUTH-DASH-1",
            "service_type": "Physical Therapy",
            "units_approved": 10,
            "units_used": 1,
            "effective_date": str(date.today() - timedelta(days=10)),
            "expiration_date": str(date.today() + timedelta(days=5)),
            "status": "active",
        },
        headers=auth_specialist_headers,
    )

    response = client.get("/api/v1/dashboard/metrics", headers=ops_manager_headers)
    assert response.json()["data"]["expiring_authorizations"] == 1
