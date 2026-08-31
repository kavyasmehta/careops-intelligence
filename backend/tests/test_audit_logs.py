def test_creating_a_client_writes_an_audit_log_entry(client, intake_headers, ops_manager_headers):
    created = client.post(
        "/api/v1/clients",
        json={
            "first_name": "Sam",
            "last_name": "Rivera",
            "date_of_birth": "1985-03-12",
            "member_id": "M-AUDIT-1",
            "status": "active",
        },
        headers=intake_headers,
    ).json()["data"]

    logs = client.get(
        f"/api/v1/audit-logs?entity_type=client&entity_id={created['id']}", headers=ops_manager_headers
    ).json()["data"]

    assert len(logs) == 1
    assert logs[0]["action"] == "create"
    assert logs[0]["user"] == "Test Intake Specialist"
    assert logs[0]["new_value"]["member_id"] == "M-AUDIT-1"
