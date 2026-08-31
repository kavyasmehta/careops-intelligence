# CareOps Intelligence — Phase 1 Plan (Product & Architecture)

## Context

The user wants a second, more ambitious portfolio project — "CareOps Intelligence," a fictional healthcare-operations SaaS — to demonstrate full-stack, data-engineering, graph-database, and AI skills for a Data Analyst/Data Scientist job search. The user's own prompt is already a near-complete spec (entities, stack, pages, phases). This document is Phase 1 only: it translates that spec into a concrete, environment-fitted plan and pauses for approval before any code is written, exactly as instructed. Implementation will then proceed one phase at a time with a run/test/verify checkpoint after each phase — this is a multi-week-scope project compressed into incremental sessions, not a single build.

## Environment findings (from inspecting this machine)

- **Node.js/npm: not installed.** Will install via Homebrew (`brew install node`) in Phase 2 — needed for the Next.js frontend.
- **Docker Desktop 29.2.1 + Compose v5.0.2: already installed.** Docker Compose is fully viable and will be used for the whole stack (Mongo, Neo4j, backend, frontend) for a professional one-command local setup.
- **MongoDB (native, port 27017) and Neo4j Desktop (bolt 7687 / http 7474) are already running** — but for the *unrelated* prior portfolio project (`job-market-skills-graph`). To avoid conflicts and keep both projects independently runnable, CareOps will run its **own** Mongo + Neo4j inside Docker Compose on different host ports: Mongo `27018→27017`, Neo4j bolt `7688→7687`, Neo4j http `7475→7474`.
- **Python 3.13.9, git, and gh (authenticated as `kavyasmehta`)** are already set up and will be reused.
- New project location: `/Users/Shared/careops-intelligence`, pushed to a new public GitHub repo `careops-intelligence`.

## Resolved decision

**Deployment scope (asked and answered):** Local + deployment-ready only. The app runs fully locally via Docker Compose; Dockerfiles/env docs/CI are production-grade and deploy-ready, but no live Vercel/Render/Atlas/Aura accounts will be created. Matches the scope chosen for the prior project.

## 1. Business problem

Healthcare operations teams (intake, authorizations, care coordination) track clients, insurance eligibility, prior authorizations, appointments, and follow-up tasks across spreadsheets, email, and disconnected systems. Nothing surfaces "what needs attention today" or explains *why* a case is risky. CareOps Intelligence centralizes this into one operational system of record with an explainable risk score, automatic alerting, and analytics — the kind of internal tool a healthcare ops team would actually pay for. All data is synthetic; the app carries a visible non-clinical disclaimer everywhere relevant (login/demo entry, footer, case-summary output).

## 2. Architecture

```
Browser
  │
  ▼
Next.js 14 (App Router, TS, Tailwind, shadcn/ui)  — frontend/
  │  REST/JSON, X-Demo-Role header
  ▼
FastAPI (Python)                                   — backend/
  ├── routers/        (thin HTTP layer, no business logic)
  ├── services/        risk scoring, alert rules, analytics, CSV export,
  │                     case-summary (template + optional LLM interface)
  ├── repositories/    Mongo (Motor, async) + Neo4j (official driver) access
  └── core/            config (pydantic-settings), structured logging
        │                       │
        ▼                       ▼
   MongoDB                  Neo4j
   (source of truth,        (relationship graph — thin nodes,
    all full records)        synced on write from services)
```

- **Demo auth**: no real login. A role switcher sets a role (Operations Manager / Intake Specialist / Authorization Specialist) client-side; every request sends `X-Demo-Role`, validated server-side against a per-route allowlist via a FastAPI dependency (`get_current_role`). This isolates the auth *seam* so real auth (JWT/OAuth) can later replace just that one dependency — no other code changes.
- **Mongo is the source of truth** for every entity. **Neo4j holds thin relationship nodes** (id + display fields only, e.g. `Client{id, name}`) — never full documents — updated idempotently by the same service layer that writes to Mongo (a `sync_graph()` call after each relevant write, and in bulk during seeding). This avoids dual-write consistency becoming its own project.
- **Risk scoring & alerts** are plain rule-based Python services, fully deterministic and unit-testable — no ML in the MVP, as specified.

## 3. Repository structure

```
careops-intelligence/
├── frontend/
│   ├── app/                 # Next.js App Router pages (see UI map below)
│   ├── components/          # shadcn/ui-based components, shared widgets
│   ├── lib/                 # api client, utils
│   ├── hooks/
│   ├── types/                # TS types mirroring backend schemas
│   └── tests/                 # component tests + Playwright e2e
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/             # config.py, logging.py, roles.py
│   │   ├── db/                 # mongo.py, neo4j.py (connection lifecycles)
│   │   ├── models/            # Pydantic domain models
│   │   ├── schemas/           # request/response DTOs
│   │   ├── repositories/      # one per collection + graph_repository.py
│   │   ├── services/          # risk_scoring.py, alert_rules.py, analytics.py,
│   │   │                        case_summary.py, csv_export.py
│   │   ├── routers/           # clients.py, eligibility.py, authorizations.py,
│   │   │                        appointments.py, alerts.py, tasks.py, notes.py,
│   │   │                        dashboard.py, analytics.py, graph.py, health.py
│   │   └── graph/             # cypher.py (named, documented queries)
│   └── tests/                 # pytest — unit + integration
├── scripts/
│   ├── seed_mongo.py           # Faker-based, fixed seed, idempotent (clears first)
│   ├── seed_neo4j.py           # builds graph from seeded Mongo data
│   └── run_seed.sh
├── docs/
│   ├── architecture.md, data-model.md, graph-model.md, api.md
│   └── screenshots/
├── .github/workflows/ci.yml    # lint + pytest + frontend build, on push
├── docker-compose.yml           # mongo, neo4j, backend, frontend
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

## 4. MongoDB data model

All documents get `created_at`/`updated_at` (UTC). IDs are Mongo ObjectIds exposed as strings over the API (never leak raw `_id` typing to the frontend — schemas convert).

| Collection | Key fields (beyond spec'd entity fields) | Indexes | Why |
|---|---|---|---|
| `clients` | as specified | `member_id` (unique), `assigned_employee_id`, `status`, `assigned_team_id`, text index on `first_name+last_name` | member_id lookups are frequent and must be unique; status/assignment power the work queue and directory filters |
| `eligibility_checks` | `client_id` ref | `client_id`, `coverage_status`, `check_date` desc | "latest check per client" and "failed checks queue" are the two hottest queries |
| `authorizations` | `client_id`, `payer` ref | `client_id`, `expiration_date`, `status`, compound `(status, expiration_date)` | expiring/expired authorization queries drive the tracker page and alert generation |
| `appointments` | `client_id`, `authorization_id` ref | `client_id`, `appointment_datetime`, `status`, `provider` | date-range and provider filters on the monitor page |
| `alerts` | `client_id` ref | compound `(status, severity)`, `assigned_employee_id`, `client_id`, and a compound `(client_id, alert_type)` used to prevent duplicate active alerts | alert center sorts/filters by severity+status constantly; dedup check must be O(1) via index |
| `tasks` | `client_id`, `assigned_employee_id` | `status`, `due_date`, `assigned_employee_id` | overdue-task queries and per-employee workload |
| `case_notes` | `client_id`, `author` | `client_id`, `created_at` desc | client-360 timeline reads notes in reverse chronological order |
| `audit_logs` | `entity_type`, `entity_id` | `(entity_type, entity_id)`, `timestamp` desc | client-360 audit tab and general audit trail queries |
| `users` | id, name, role, team_id (demo users only, no passwords) | `role` | role switcher lookup |

Schema validation: each collection gets a JSON Schema `$jsonSchema` validator (required fields + enums for status/severity/role fields) applied via `db.command("collMod", ...)` in the seed/setup script — catches bad writes at the DB layer, not just in Pydantic.

## 5. Neo4j graph model

**Nodes** (thin — id + minimal display fields only): `Client`, `Employee`, `Team`, `Payer`, `Provider`, `Service`, `Appointment`, `Authorization`, `RiskFactor`

**Relationships:**
```
(Client)-[:CLIENT_HAS_APPOINTMENT]->(Appointment)
(Appointment)-[:APPOINTMENT_WITH_PROVIDER]->(Provider)
(Appointment)-[:APPOINTMENT_REQUIRES_AUTHORIZATION]->(Authorization)
(Client)-[:CLIENT_COVERED_BY_PAYER]->(Payer)
(Authorization)-[:AUTHORIZATION_FOR_SERVICE]->(Service)
(Client)-[:CLIENT_ASSIGNED_TO_EMPLOYEE]->(Employee)
(Employee)-[:EMPLOYEE_MEMBER_OF_TEAM]->(Team)
(Client)-[:CLIENT_HAS_RISK_FACTOR]->(RiskFactor)
```

Constraints: uniqueness on each node's `id`. Sync strategy: `graph_repository.py` exposes idempotent `MERGE`-based upsert functions called (a) in bulk by `seed_neo4j.py` and (b) individually by services after a relevant Mongo write (new appointment, new authorization, assignment change, new risk factor).

**The 5 required business queries, mapped:**
1. *Upcoming appointment, no valid authorization* → `MATCH (c:Client)-[:CLIENT_HAS_APPOINTMENT]->(a:Appointment) WHERE a.datetime > $now AND NOT EXISTS { (a)-[:APPOINTMENT_REQUIRES_AUTHORIZATION]->(:Authorization {status:'active'}) } RETURN c`
2. *Providers connected to the most unresolved authorization cases* → traverse `Provider<-Appointment<-...-Authorization{status:'expired'|'exhausted'}`, `count()` + `ORDER BY DESC`
3. *Payer with most failed eligibility checks* → this one needs the failure fact itself, which lives in Mongo (`eligibility_checks.coverage_status`); the graph models `Client-[:CLIENT_COVERED_BY_PAYER]->Payer`, so the query joins graph client→payer edges against a Mongo-derived failed-client-id set passed in as a parameter — documented clearly as a hybrid query, not pretending Neo4j alone answers it.
4. *Employees with highest-risk workload* → `MATCH (e:Employee)<-[:CLIENT_ASSIGNED_TO_EMPLOYEE]-(c:Client)-[:CLIENT_HAS_RISK_FACTOR]->(r) RETURN e, count(r)` ordered desc.
5. *Clients with similar risk patterns* → clients sharing `RiskFactor` nodes: `MATCH (c1:Client)-[:CLIENT_HAS_RISK_FACTOR]->(rf)<-[:CLIENT_HAS_RISK_FACTOR]-(c2:Client) WHERE c1 <> c2 RETURN c1, c2, collect(rf) ...` — powers the Network Intelligence page's "similar cases" panel.

## 6. API endpoint plan (all under `/api/v1`)

Consistent envelope: `{"data": ..., "meta": {"page", "page_size", "total"}}` for lists, `{"data": ...}` for single items, `{"error": {"code", "message", "details"}}` for errors. All list endpoints support `page`, `page_size`, `sort`, and resource-appropriate filters + `q` search.

- `GET /health` — liveness + Mongo/Neo4j connectivity check
- `clients`: `GET/POST /clients`, `GET/PATCH /clients/{id}`, `GET /clients/{id}/summary` (case-summary generator), `GET /clients/{id}/graph` (ego network)
- `eligibility`: `GET/POST /eligibility-checks`, filters incl. `coverage_status`
- `authorizations`: `GET/POST /authorizations`, `GET/PATCH /authorizations/{id}`, `GET /authorizations/expiring?within_days=`
- `appointments`: `GET/POST /appointments`, `GET/PATCH /appointments/{id}`
- `alerts`: `GET /alerts`, `PATCH /alerts/{id}` (assign/resolve), dedup enforced server-side
- `tasks`: `GET/POST /tasks`, `PATCH /tasks/{id}`
- `case-notes`: `GET/POST /case-notes`
- `audit-logs`: `GET /audit-logs` (filter by entity)
- `dashboard`: `GET /dashboard/metrics` (executive dashboard aggregates, filterable by date range/team/payer/status)
- `analytics`: `GET /analytics/*` (trends, payer performance, workload, resolution time), `GET /analytics/export.csv`
- `risk`: `GET /clients/{id}/risk` (score + factor breakdown), consistent with a single documented `risk_scoring.py` service
- `graph`: `GET /graph/insights/*` for the 5 named business queries
- Central FastAPI exception handlers → consistent error envelope + correct status codes (404/409/422/500); auto OpenAPI docs at `/docs`.

## 7. UI page map (Next.js App Router)

```
/                      → demo entry / role switcher (branded, disclaimer)
/dashboard             → executive dashboard
/queue                 → operations work queue
/clients               → client directory
/clients/[id]          → client 360 (tabs: overview, eligibility, authorizations,
                          appointments, alerts+tasks, notes, audit, graph)
/eligibility           → eligibility center
/authorizations        → authorization tracker
/appointments          → appointment monitor
/alerts                → alert center
/network               → network intelligence (focused graph view + insights)
/analytics             → analytics + CSV export
```
Shared shell: collapsible sidebar, role indicator, light/dark toggle, toast/dialog primitives from shadcn/ui, persistent disclaimer banner.

## 8. Phased implementation checklist

Following the user's exact sequence, one phase at a time, each ending with: run app, run tests, fix errors, summarize, explain how to verify.

1. **Product & architecture** — this document (current phase)
2. **Local infrastructure** — scaffolding, Docker Compose (Mongo+Neo4j+backend+frontend), env config, health checks
3. **Backend foundation** — models/schemas/repositories/services/routers for all core entities, validation, error handling, pytest
4. **Synthetic data** — Faker seed script (fixed seed, ~250 clients/5 payers/etc. per spec, intentional problem scenarios), seeds Mongo + Neo4j consistently
5. **Frontend foundation** — app shell, nav, design system, role switcher, typed API client, loading/error states
6. **Core workflows** — dashboard, work queue, client directory, client 360, eligibility center, authorization tracker, appointment monitor, alert center
7. **Analytics & graph intelligence** — analytics page, CSV export, graph queries, network intelligence page
8. **Risk & automation** — explainable risk scoring service, automatic alert generation, case-summary generator (template-first, LLM optional behind env flag)
9. **Quality & delivery** — backend/frontend/e2e tests, accessibility + responsive review, full documentation, deployment configs, screenshots

## 9. Risks / scope concerns

- **This is a genuinely multi-week project** condensed into iterative phases; each phase is independently runnable and demoable so the repo is never in a broken state between sessions.
- **Graph/Mongo consistency**: mitigated by keeping Neo4j nodes thin and updates idempotent (`MERGE`), never a second source of truth.
- **AI feature**: template-based summary ships first and always works with zero API keys; a real LLM is an explicit opt-in behind an interface + env var, never required.
- **No real auth**: demo role switcher only — clearly a portfolio simplification, called out in the README's limitations section.
- **Full polish items** (Playwright e2e, CI, dark mode, accessibility pass) are scheduled for Phase 9 rather than spread throughout, to keep early phases shippable quickly.

## 10. Questions

The one materially architecture-affecting question (deployment scope) has been asked and answered above. Everything else in this document is a sensible default chosen to fit the spec and this machine's environment; flagged clearly so the user can redirect anything before Phase 2 begins.

**Next step on approval:** begin Phase 2 (local infrastructure) only, then stop for the user to verify before Phase 3.
