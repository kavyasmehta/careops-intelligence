def _make_client(client, intake_headers, member_id):
    return client.post(
        "/api/v1/clients",
        json={
            "first_name": "Summary",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "member_id": member_id,
            "status": "active",
        },
        headers=intake_headers,
    ).json()["data"]


def test_summary_uses_template_by_default(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-SUMMARY-1")
    response = client.get(f"/api/v1/clients/{created['id']}/summary", headers=ops_manager_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["generated_by"] == "template"
    assert "not a clinical" in data["disclaimer"].lower()
    assert "Summary Test" in data["summary"]


def test_summary_reflects_failed_eligibility(client, ops_manager_headers, intake_headers):
    created = _make_client(client, intake_headers, "M-SUMMARY-2")
    client.post(
        "/api/v1/eligibility-checks",
        json={
            "client_id": created["id"],
            "payer": "Molina Healthcare",
            "check_date": "2026-01-01T00:00:00Z",
            "coverage_status": "failed",
            "failure_reason": "Plan not active for requested service",
        },
        headers=intake_headers,
    )

    response = client.get(f"/api/v1/clients/{created['id']}/summary", headers=ops_manager_headers)
    summary = response.json()["data"]["summary"]
    assert "FAILED" in summary
    assert "Molina Healthcare" in summary


def test_summary_404_for_unknown_client(client, ops_manager_headers):
    response = client.get("/api/v1/clients/64b64c1f2f3a4b5c6d7e8f90/summary", headers=ops_manager_headers)
    assert response.status_code == 404
