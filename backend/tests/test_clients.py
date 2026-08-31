def make_client_payload(member_id="M-1001"):
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1990-05-01",
        "member_id": member_id,
        "email": "jane.doe@example.com",
        "phone": "555-0100",
        "address": {"line1": "123 Main St", "city": "Baltimore", "state": "MD", "zip": "21201"},
        "status": "active",
    }


def test_create_client_success(client, intake_headers):
    response = client.post("/api/v1/clients", json=make_client_payload(), headers=intake_headers)
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["member_id"] == "M-1001"
    assert body["status"] == "active"
    assert "id" in body and "created_at" in body


def test_create_client_duplicate_member_id_is_conflict(client, intake_headers):
    client.post("/api/v1/clients", json=make_client_payload(), headers=intake_headers)
    response = client.post("/api/v1/clients", json=make_client_payload(), headers=intake_headers)
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]["message"]


def test_create_client_wrong_role_is_forbidden(client, auth_specialist_headers):
    response = client.post("/api/v1/clients", json=make_client_payload(), headers=auth_specialist_headers)
    assert response.status_code == 403


def test_create_client_missing_required_field_is_422(client, intake_headers):
    payload = make_client_payload()
    del payload["member_id"]
    response = client.post("/api/v1/clients", json=payload, headers=intake_headers)
    assert response.status_code == 422


def test_get_client_not_found_is_404(client, ops_manager_headers):
    response = client.get("/api/v1/clients/64b64c1f2f3a4b5c6d7e8f90", headers=ops_manager_headers)
    assert response.status_code == 404


def test_list_and_update_client(client, intake_headers, ops_manager_headers):
    created = client.post("/api/v1/clients", json=make_client_payload(), headers=intake_headers).json()["data"]

    listed = client.get("/api/v1/clients", headers=ops_manager_headers)
    assert listed.status_code == 200
    assert listed.json()["meta"]["total"] == 1

    updated = client.patch(
        f"/api/v1/clients/{created['id']}", json={"status": "inactive"}, headers=intake_headers
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "inactive"
