def make_alert_payload(**overrides):
    payload = {
        "client_id": "64b64c1f2f3a4b5c6d7e8f90",
        "alert_type": "authorization_expiring",
        "severity": "high",
        "explanation": "Authorization AUTH-1 expires in 5 days",
        "recommended_action": "Contact payer to renew authorization",
    }
    payload.update(overrides)
    return payload


def test_create_alert_success(client, ops_manager_headers):
    response = client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers)
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "open"


def test_duplicate_active_alert_is_conflict(client, ops_manager_headers):
    client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers)
    response = client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers)
    assert response.status_code == 409


def test_new_alert_allowed_after_previous_resolved(client, ops_manager_headers):
    first = client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers).json()["data"]
    client.patch(f"/api/v1/alerts/{first['id']}", json={"status": "resolved"}, headers=ops_manager_headers)

    response = client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers)
    assert response.status_code == 201


def test_resolving_alert_sets_resolved_at(client, ops_manager_headers):
    created = client.post("/api/v1/alerts", json=make_alert_payload(), headers=ops_manager_headers).json()["data"]
    assert created["resolved_at"] is None

    resolved = client.patch(
        f"/api/v1/alerts/{created['id']}", json={"status": "resolved"}, headers=ops_manager_headers
    ).json()["data"]
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None
