#!/usr/bin/env bash
# Seeds MongoDB, then builds the Neo4j graph from it. Safe to rerun —
# both steps clear their target store first.
set -e
cd "$(dirname "$0")/.."

source backend/.venv/bin/activate
python scripts/seed_mongo.py
echo
python scripts/seed_neo4j.py
