# Recruiter-friendly summary

**CareOps Intelligence** — a full-stack healthcare operations platform built end-to-end (product design → data modeling → backend → frontend → testing → CI) to demonstrate the skills behind a Data Analyst / Data Scientist / full-stack role.

**In one sentence:** a Next.js + FastAPI + MongoDB + Neo4j application that tracks healthcare clients, insurance eligibility, and authorizations; scores each client's operational risk with a fully explainable rule-based model; automatically raises alerts when something needs attention; and answers relationship-shaped questions (which providers, which payers, which employees are overloaded) with a graph database — all on reproducible synthetic data with zero real PHI.

**Why it's a strong signal for this kind of role:**

- **Data modeling judgment** — deliberately split data between MongoDB (source of truth, document-shaped operational records) and Neo4j (thin relationship graph), and documented *why* each of the 5 required business questions belongs to graph traversal, plain aggregation, or a hybrid of both.
- **Explainable analytics over black-box ML** — the risk score is a transparent, auditable point system rather than a model, which is the right call for an operational tool a non-technical case worker has to trust and act on.
- **Real engineering discipline** — layered backend architecture (routers/services/repositories), typed frontend, 48 backend tests + 14 frontend tests + a full Playwright end-to-end workflow, CI running all of it against live Mongo/Neo4j containers on every push.
- **Responsible AI integration** — the AI case-summary feature is designed to always work with zero API keys (deterministic template) and only calls a real LLM behind an explicit opt-in flag, never sends data externally by default, and never issues clinical recommendations.
- **Shipped, not just designed** — 9 phases built incrementally, each one runnable and tested before moving to the next; bugs found via real end-to-end testing (not just manual clicking) were traced and fixed, not hand-waved.

**Live artifacts:** full source on GitHub (see the main [README](../README.md)), screenshots of every major page, `/docs` OpenAPI documentation, and a documented Neo4j graph model with 5 named business-intelligence queries.

## Resume bullet points

- Designed and built **CareOps Intelligence**, a full-stack healthcare operations platform (Next.js/TypeScript, FastAPI/Python, MongoDB, Neo4j) modeling clients, insurance eligibility, prior authorizations, and appointments across 250+ synthetic client records.
- Designed a dual-database architecture using **MongoDB as the system of record and Neo4j for relationship analytics**, with idempotent graph synchronization and 5 documented Cypher queries answering business questions (authorization risk, provider workload, payer performance, employee caseload, similar-risk cohorts).
- Built an **explainable, rule-based risk-scoring engine** (0–100, weighted named factors) and an **automatic alert-generation pipeline** with duplicate prevention, replacing what would otherwise require manual case review across hundreds of active clients.
- Implemented a **pluggable AI case-summary feature** using a provider interface pattern — a zero-dependency deterministic template by default, with an optional LLM-backed provider gated behind an environment variable and async-safe execution (`asyncio.to_thread`).
- Wrote **48 backend Pytest tests, 14 frontend Vitest/RTL tests, and a full Playwright end-to-end regression workflow**, wired into GitHub Actions CI against live MongoDB and Neo4j service containers; used the e2e suite to find and fix a real UI defect (mislabeled filter dropdowns) missed by manual testing.
- Built a responsive, accessible Next.js frontend (TanStack Table, Recharts, React Hook Form + Zod, shadcn/ui) with light/dark themes, loading/empty/error states, and a demo role-switcher authentication seam designed for a clean swap to real auth.
