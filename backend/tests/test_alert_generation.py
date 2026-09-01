from datetime import date, timedelta


def _make_client(client, intake_headers, member_id):
    return client.post(
        "/api/v1/clients",
        json={
            "first_name": "Gen",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "member_id": member_id,
            "status": "active",
        },
        headers=intake_headers,
    ).json()["data"]


def test_generation_creates_alert_for_failed_eligibility(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-GEN-1")
    client.post(
        "/api/v1/eligibility-checks",
        json={
            "client_id": created["id"],
            "payer": "Cigna",
            "check_date": "2026-01-01T00:00:00Z",
            "coverage_status": "failed",
            "failure_reason": "Member ID not found",
        },
        headers=intake_headers,
    )

    response = client.post("/api/v1/alerts/generate", headers=ops_manager_headers)
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["alerts_created"] >= 1
    assert result["created_by_type"].get("eligibility_failed", 0) >= 1

    alerts = client.get(f"/api/v1/alerts?client_id={created['id']}", headers=ops_manager_headers).json()["data"]
    assert any(a["alert_type"] == "eligibility_failed" for a in alerts)


def test_generation_is_idempotent_no_duplicate_alerts(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-GEN-2")
    client.post(
        "/api/v1/eligibility-checks",
        json={
            "client_id": created["id"],
            "payer": "Cigna",
            "check_date": "2026-01-01T00:00:00Z",
            "coverage_status": "failed",
            "failure_reason": "Member ID not found",
        },
        headers=intake_headers,
    )

    first = client.post("/api/v1/alerts/generate", headers=ops_manager_headers).json()["data"]
    second = client.post("/api/v1/alerts/generate", headers=ops_manager_headers).json()["data"]

    assert first["alerts_created"] >= 1
    assert second["created_by_type"].get("eligibility_failed", 0) == 0
    assert second["alerts_skipped_as_duplicate"] >= first["alerts_created"]

    alerts = client.get(
        f"/api/v1/alerts?client_id={created['id']}&severity=high", headers=ops_manager_headers
    ).json()["data"]
    eligibility_alerts = [a for a in alerts if a["alert_type"] == "eligibility_failed"]
    assert len(eligibility_alerts) == 1


def test_generation_only_ops_manager(client, intake_headers):
    response = client.post("/api/v1/alerts/generate", headers=intake_headers)
    assert response.status_code == 403


def test_generation_creates_authorization_expiring_alert(client, ops_manager_headers, intake_headers, auth_specialist_headers):
    created = _make_client(client, intake_headers, "M-GEN-3")
    client.post(
        "/api/v1/authorizations",
        json={
            "client_id": created["id"],
            "payer": "Aetna",
            "authorization_number": "AUTH-GEN-1",
            "service_type": "Physical Therapy",
            "units_approved": 10,
            "units_used": 2,
            "effective_date": str(date.today() - timedelta(days=10)),
            "expiration_date": str(date.today() + timedelta(days=5)),
            "status": "active",
        },
        headers=auth_specialist_headers,
    )

    result = client.post("/api/v1/alerts/generate", headers=ops_manager_headers).json()["data"]
    assert result["created_by_type"].get("authorization_expiring", 0) >= 1
