# CareOps Intelligence

A portfolio-quality healthcare **operations management and analytics platform** for a fictional healthcare organization — built to demonstrate full-stack development, data modeling, graph analytics, and applied AI.

> **Portfolio demonstration using synthetic data. Not intended for clinical use or storage of protected health information.**

## Status

🚧 Under active, phased development. Current phase: **Phase 7 — Analytics and graph intelligence**. All 8 core workflow pages (Phase 6) are live, plus: an **Analytics** page (resolution-time-by-severity, authorization/eligibility outcome distributions, team workload, a 12-week alerts trend, and CSV export for 5 entities) and a **Network Intelligence** page answering all 5 required graph business questions (payer failure rates, employee risk workload, providers with unresolved cases, similar-clients-by-risk-pattern) plus a focused, hand-rolled radial visualization of any one client's relationship network. See [`docs/architecture.md`](docs/architecture.md) for the full product plan and phased checklist.

A complete project summary, architecture diagram, screenshots, and UI will land here as later phases complete.

## Quick start (current phase)

Requires Docker Desktop.

```bash
cp .env.example .env
docker compose up --build
```

- Backend health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Frontend infra-check page: http://localhost:3000
- Neo4j Browser: http://localhost:7475 (user `neo4j`, password from `.env`)

### Seeding synthetic data

Once the containers are up:

```bash
./scripts/run_seed.sh
```

This generates ~250 clients, 1,000 eligibility checks, 500 authorizations, 1,000 appointments, ~300 alerts, 500 tasks, and 1,000 case notes into MongoDB (fixed random seed — safe to rerun), then builds the corresponding Neo4j graph from that data. See [`docs/architecture.md`](docs/architecture.md) for the reasoning behind the data model and graph model.

## Tech stack

Next.js (TypeScript, App Router, Tailwind, shadcn/ui) · FastAPI (Python) · MongoDB · Neo4j · Docker Compose

## License / disclaimer

All data in this project is synthetic and generated for demonstration purposes only.
