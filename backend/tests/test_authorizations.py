def make_authorization_payload(**overrides):
    payload = {
        "client_id": "64b64c1f2f3a4b5c6d7e8f90",
        "payer": "Aetna",
        "authorization_number": "AUTH-1",
        "service_type": "Physical Therapy",
        "units_approved": 10,
        "units_used": 2,
        "effective_date": "2026-01-01",
        "expiration_date": "2026-06-01",
        "status": "active",
    }
    payload.update(overrides)
    return payload


def test_create_authorization_success(client, auth_specialist_headers):
    response = client.post(
        "/api/v1/authorizations", json=make_authorization_payload(), headers=auth_specialist_headers
    )
    assert response.status_code == 201
    assert response.json()["data"]["authorization_number"] == "AUTH-1"


def test_expiration_before_effective_date_is_422(client, auth_specialist_headers):
    payload = make_authorization_payload(effective_date="2026-06-01", expiration_date="2026-01-01")
    response = client.post("/api/v1/authorizations", json=payload, headers=auth_specialist_headers)
    assert response.status_code == 422


def test_units_used_exceeding_approved_is_422(client, auth_specialist_headers):
    payload = make_authorization_payload(units_approved=5, units_used=10)
    response = client.post("/api/v1/authorizations", json=payload, headers=auth_specialist_headers)
    assert response.status_code == 422


def test_wrong_role_cannot_create_authorization(client, intake_headers):
    response = client.post(
        "/api/v1/authorizations", json=make_authorization_payload(), headers=intake_headers
    )
    assert response.status_code == 403


def test_expiring_authorizations_endpoint(client, auth_specialist_headers, ops_manager_headers):
    client.post(
        "/api/v1/authorizations",
        json=make_authorization_payload(
            authorization_number="AUTH-SOON", effective_date="2026-08-01", expiration_date="2026-09-15"
        ),
        headers=auth_specialist_headers,
    )
    client.post(
        "/api/v1/authorizations",
        json=make_authorization_payload(
            authorization_number="AUTH-LATER", effective_date="2026-08-01", expiration_date="2099-01-01"
        ),
        headers=auth_specialist_headers,
    )
    # within_days=30 should surface the one expiring soon and exclude the
    # one expiring decades from now — that's the actual point of the filter.
    response = client.get("/api/v1/authorizations/expiring?within_days=30", headers=ops_manager_headers)
    assert response.status_code == 200
    numbers = {item["authorization_number"] for item in response.json()["data"]}
    assert "AUTH-SOON" in numbers
    assert "AUTH-LATER" not in numbers
