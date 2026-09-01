# CareOps Intelligence

A portfolio-quality healthcare **operations management and analytics platform** for a fictional healthcare organization — built to demonstrate full-stack development, data modeling, graph analytics, and applied AI.

> **Portfolio demonstration using synthetic data. Not intended for clinical use or storage of protected health information.**

## Status

🚧 Under active, phased development. Current phase: **Phase 8 — Risk & automation**. Adds: an explainable, rule-based **operational risk score** (0–100, Low/Medium/High/Critical, every point traceable to a named factor) shown on each client's profile; a **one-click alert-generation sweep** (Operations Manager only) that scans all clients for the 7 spec'd conditions and creates any missing alerts, safe to re-run without creating duplicates; and an **AI case-summary generator** that always works with zero API keys (deterministic template) with an LLM rewrite available strictly as an opt-in behind an env var, clearly labeled either way and never issuing clinical recommendations. See [`docs/architecture.md`](docs/architecture.md) for the full product plan and phased checklist.

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
