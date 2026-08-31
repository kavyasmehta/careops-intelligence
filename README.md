# CareOps Intelligence

A portfolio-quality healthcare **operations management and analytics platform** for a fictional healthcare organization — built to demonstrate full-stack development, data modeling, graph analytics, and applied AI.

> **Portfolio demonstration using synthetic data. Not intended for clinical use or storage of protected health information.**

## Status

🚧 Under active, phased development. Current phase: **Phase 2 — Local infrastructure** (Docker Compose, database connections, health checks). See [`docs/architecture.md`](docs/architecture.md) for the full product plan.

A complete project summary, architecture diagram, data models, screenshots, and setup guide will land here as each phase completes — see the phased checklist in the architecture doc for what's built vs. planned.

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

## Tech stack

Next.js (TypeScript, App Router, Tailwind, shadcn/ui) · FastAPI (Python) · MongoDB · Neo4j · Docker Compose

## License / disclaimer

All data in this project is synthetic and generated for demonstration purposes only.
