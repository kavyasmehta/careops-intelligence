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

- **Backend** (48 Pytest tests — CRUD, validation, risk scoring, alert generation, dashboard/analytics, graph queries):
  ```bash
  cd backend && source .venv/bin/activate && pytest
  ```
- **Frontend unit tests** (Vitest + React Testing Library, 14 tests — forms, work-queue actions, client-profile rendering, loading/error states):
  ```bash
  cd frontend && npm run test        # single run
  cd frontend && npm run test:watch  # watch mode while iterating
  ```
- **End-to-end** (Playwright, against the real running stack — requires `docker compose up` and seeded data first):
  ```bash
  cd frontend && npm run test:e2e
  ```
  The e2e spec resolves a real alert as part of the workflow it verifies, so re-run `./scripts/run_seed.sh` afterward before using the app for a demo.

Run the relevant test suite before committing anything that touches `app/services/`, API contracts, or shared frontend components (especially `FilterSelect` and other `components/ui` primitives — see the Base UI gotchas below).

## Base UI gotchas (shadcn/ui is built on Base UI, not Radix, here)

- Use Base UI's `render` prop for composition, not Radix's `asChild`.
- `SelectValue` does not automatically track a matched `SelectItem`'s rendered label — pass a `children` render function, e.g. `<SelectValue>{(value) => label}</SelectValue>`. It also won't reactively update on an externally-changed `value` prop without a `key` forcing remount.
- Prefer the shared `components/filter-select.tsx` for any "All X" style filter dropdown — it already encodes the fix above; don't re-derive it per page.

## Environment variables

Never commit a real `.env` file. `.env.example` is the source of truth for what variables exist — update it whenever you add a new one.
