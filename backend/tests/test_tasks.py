def make_task_payload(**overrides):
    payload = {
        "title": "Follow up on eligibility failure",
        "client_id": "64b64c1f2f3a4b5c6d7e8f90",
        "assigned_employee_id": "64b64c1f2f3a4b5c6d7e8f91",
        "priority": "high",
        "due_date": "2020-01-01",  # deliberately in the past
    }
    payload.update(overrides)
    return payload


def test_past_due_open_task_is_flagged_overdue(client, ops_manager_headers):
    response = client.post("/api/v1/tasks", json=make_task_payload(), headers=ops_manager_headers)
    assert response.status_code == 201
    assert response.json()["data"]["is_overdue"] is True


def test_future_due_task_is_not_overdue(client, ops_manager_headers):
    response = client.post(
        "/api/v1/tasks", json=make_task_payload(due_date="2099-01-01"), headers=ops_manager_headers
    )
    assert response.json()["data"]["is_overdue"] is False


def test_completing_task_sets_completed_at_and_clears_overdue(client, ops_manager_headers):
    created = client.post("/api/v1/tasks", json=make_task_payload(), headers=ops_manager_headers).json()["data"]
    assert created["is_overdue"] is True

    completed = client.patch(
        f"/api/v1/tasks/{created['id']}", json={"status": "completed"}, headers=ops_manager_headers
    ).json()["data"]
    assert completed["completed_at"] is not None
    assert completed["is_overdue"] is False
