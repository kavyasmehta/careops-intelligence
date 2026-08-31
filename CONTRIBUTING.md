# Contributing to CareOps Intelligence

This is a solo portfolio project, but it follows real engineering practices so it reads like a maintained codebase.

## Local setup

See the [README](README.md) quick start. In short: `cp .env.example .env` then `docker compose up --build`.

For faster backend iteration without Docker:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

For frontend iteration without Docker:
```bash
cd frontend
npm install
npm run dev
```

## Code style

- **Backend**: routes stay thin — HTTP concerns only. Business logic lives in `app/services/`, data access in `app/repositories/`. All request/response shapes are explicit Pydantic schemas in `app/schemas/`.
- **Frontend**: strict TypeScript, no `any`. Shared UI comes from `components/ui` (shadcn/ui); feature components live under `components/`.
- **Commits**: small, meaningful commits per phase/feature. Present tense, imperative mood ("Add authorization tracker page", not "Added...").

## Tests

- Backend: `cd backend && source .venv/bin/activate && pytest`
- Frontend: `cd frontend && npm test` (added in Phase 9)
- End-to-end: `cd frontend && npx playwright test` (added in Phase 9)

Run tests before committing anything that touches `app/services/` or API contracts.

## Environment variables

Never commit a real `.env` file. `.env.example` is the source of truth for what variables exist — update it whenever you add a new one.
