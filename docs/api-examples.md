# Sample API requests

All endpoints are under `/api/v1` (except `/health`). Full interactive docs live at **http://localhost:8000/docs** whenever the backend is running.

## Demo authentication headers

There is no real login. Every request is scoped by two optional headers:

- `X-Demo-Role` — one of `operations_manager`, `intake_specialist`, `authorization_specialist`. Defaults to `operations_manager` if omitted. Routes reject roles outside their allowlist with `403`.
- `X-Demo-User` — a free-text display name attributed to audit-log entries. Defaults to `"Demo User"` if omitted.

```bash
BASE=http://localhost:8000/api/v1
AUTH=(-H "X-Demo-Role: operations_manager" -H "X-Demo-User: Dana Whitfield")
```

## List response envelope

All list endpoints return `{"data": [...], "meta": {"page", "page_size", "total"}}`; single-item endpoints return `{"data": {...}}`; errors return `{"error": {"code", "message", "details"}}`.

## Clients

List clients, filtered and paginated:

```bash
curl -s "$BASE/clients?status=active&page=1&page_size=10" "${AUTH[@]}" | jq
```

Search by name:

```bash
curl -s "$BASE/clients?q=acosta" "${AUTH[@]}" | jq
```

Create a client:

```bash
curl -s -X POST "$BASE/clients" "${AUTH[@]}" -H "Content-Type: application/json" -d '{
  "first_name": "Jordan",
  "last_name": "Reyes",
  "date_of_birth": "1990-04-12",
  "member_id": "MBR-999001",
  "email": "jordan.reyes@example.org",
  "status": "active"
}' | jq
```

Get a client's explainable risk score:

```bash
curl -s "$BASE/clients/<client_id>/risk" "${AUTH[@]}" | jq
```

Get (or generate) the AI case summary:

```bash
curl -s "$BASE/clients/<client_id>/summary" "${AUTH[@]}" | jq
```

## Alerts

List open, critical alerts:

```bash
curl -s "$BASE/alerts?status=open&severity=critical" "${AUTH[@]}" | jq
```

Resolve an alert:

```bash
curl -s -X PATCH "$BASE/alerts/<alert_id>" "${AUTH[@]}" -H "Content-Type: application/json" -d '{
  "status": "resolved",
  "resolution_notes": "Verified with payer; coverage reinstated."
}' | jq
```

Run the automatic alert-generation sweep (Operations Manager only — scans all clients against the 7 defined conditions, skips anything that already has a matching active alert):

```bash
curl -s -X POST "$BASE/alerts/generate" "${AUTH[@]}" | jq
```

## Authorizations

Authorizations expiring soon:

```bash
curl -s "$BASE/authorizations?status=active" "${AUTH[@]}" | jq
```

## Dashboard and analytics

Executive dashboard KPIs:

```bash
curl -s "$BASE/dashboard/metrics" "${AUTH[@]}" | jq
```

Analytics overview (Operations Manager only) and CSV exports:

```bash
curl -s "$BASE/analytics/overview" "${AUTH[@]}" | jq
curl -s "$BASE/analytics/export/alerts?severity=critical" "${AUTH[@]}" -o critical-alerts.csv
```

## Graph insights

Any of the 5 named business queries, plus a client's ego network for the Network Intelligence page (all Operations-Manager-and-up):

```bash
curl -s "$BASE/graph/insights/appointments-without-authorization" "${AUTH[@]}" | jq
curl -s "$BASE/graph/insights/providers-unresolved-authorizations" "${AUTH[@]}" | jq
curl -s "$BASE/graph/insights/payer-failure-rates" "${AUTH[@]}" | jq
curl -s "$BASE/graph/insights/employee-risk-workload" "${AUTH[@]}" | jq
curl -s "$BASE/graph/insights/similar-clients/<client_id>" "${AUTH[@]}" | jq
curl -s "$BASE/graph/clients/<client_id>/ego" "${AUTH[@]}" | jq
```

## Health check

```bash
curl -s http://localhost:8000/health | jq
```
