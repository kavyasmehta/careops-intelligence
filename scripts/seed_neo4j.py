"""
Builds the Neo4j relationship graph from the already-seeded MongoDB data.

Mongo remains the source of truth; this script only derives graph
structure from it (thin nodes — id + display fields only — never full
documents), matching the architecture's sync strategy. Safe to rerun:
wipes the graph first, then rebuilds it from whatever is currently in
Mongo (run seed_mongo.py first).

RiskFactor nodes are computed with the exact same conditions used to
generate alerts in seed_mongo.py (see risk_conditions.py), so the graph's
"which clients are at risk" view and the operational alert queue always
agree with each other.
"""
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_data import PROVIDERS  # noqa: E402
from risk_conditions import compute_multiple_issues_pool, compute_risk_pools  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018")
MONGO_DB = os.getenv("MONGO_DB", "careops")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "careops-dev-password")

CONSTRAINTS = [
    "CREATE CONSTRAINT client_id IF NOT EXISTS FOR (n:Client) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT team_name IF NOT EXISTS FOR (n:Team) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT payer_name IF NOT EXISTS FOR (n:Payer) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT provider_name IF NOT EXISTS FOR (n:Provider) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT service_name IF NOT EXISTS FOR (n:Service) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT appointment_id IF NOT EXISTS FOR (n:Appointment) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT authorization_id IF NOT EXISTS FOR (n:Authorization) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT risk_factor_name IF NOT EXISTS FOR (n:RiskFactor) REQUIRE n.name IS UNIQUE",
]


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def fetch_all(db) -> dict[str, list[dict]]:
    def as_str_id(doc):
        doc = dict(doc)
        doc["id"] = str(doc.pop("_id"))
        return doc

    return {
        "users": [as_str_id(d) for d in db["users"].find({})],
        "clients": [as_str_id(d) for d in db["clients"].find({})],
        "eligibility_checks": [as_str_id(d) for d in db["eligibility_checks"].find({})],
        "authorizations": [as_str_id(d) for d in db["authorizations"].find({})],
        "appointments": [as_str_id(d) for d in db["appointments"].find({})],
        "tasks": [as_str_id(d) for d in db["tasks"].find({})],
    }


def main():
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    data = fetch_all(mongo)
    print(f"Loaded from Mongo: {', '.join(f'{k}={len(v)}' for k, v in data.items())}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        print("Wiping existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Applying constraints...")
        for stmt in CONSTRAINTS:
            session.run(stmt)

        print("Loading Team and Employee nodes...")
        session.run(
            """
            UNWIND $employees AS e
            MERGE (emp:Employee {id: e.id})
            SET emp.name = e.name, emp.role = e.role
            MERGE (t:Team {name: e.team_id})
            MERGE (emp)-[:EMPLOYEE_MEMBER_OF_TEAM]->(t)
            """,
            employees=data["users"],
        )

        print("Loading Provider and Service nodes...")
        session.run(
            """
            UNWIND $providers AS p
            MERGE (prov:Provider {name: p.name})
            SET prov.specialty = p.specialty
            MERGE (s:Service {name: p.specialty})
            """,
            providers=PROVIDERS,
        )

        distinct_services = sorted(
            {a["service_type"] for a in data["authorizations"]} | {a["service_type"] for a in data["appointments"]}
        )
        session.run("UNWIND $names AS name MERGE (:Service {name: name})", names=distinct_services)

        distinct_payers = sorted(
            {e["payer"] for e in data["eligibility_checks"]} | {a["payer"] for a in data["authorizations"]}
        )
        session.run("UNWIND $names AS name MERGE (:Payer {name: name})", names=distinct_payers)

        print(f"Loading {len(data['clients'])} Client nodes...")
        for batch in chunked(data["clients"], 500):
            session.run(
                """
                UNWIND $clients AS c
                MERGE (cl:Client {id: c.id})
                SET cl.name = c.first_name + ' ' + c.last_name, cl.status = c.status
                WITH cl, c
                WHERE c.assigned_employee_id IS NOT NULL
                MATCH (emp:Employee {id: c.assigned_employee_id})
                MERGE (cl)-[:CLIENT_ASSIGNED_TO_EMPLOYEE]->(emp)
                """,
                clients=batch,
            )

        print("Linking clients to payers (via eligibility history)...")
        client_payers = sorted({(e["client_id"], e["payer"]) for e in data["eligibility_checks"]})
        for batch in chunked([{"client_id": c, "payer": p} for c, p in client_payers], 1000):
            session.run(
                """
                UNWIND $rows AS row
                MATCH (cl:Client {id: row.client_id})
                MATCH (p:Payer {name: row.payer})
                MERGE (cl)-[:CLIENT_COVERED_BY_PAYER]->(p)
                """,
                rows=batch,
            )

        print(f"Loading {len(data['authorizations'])} Authorization nodes...")
        for batch in chunked(data["authorizations"], 500):
            session.run(
                """
                UNWIND $rows AS a
                MERGE (auth:Authorization {id: a.id})
                SET auth.authorization_number = a.authorization_number,
                    auth.status = a.status,
                    auth.expiration_date = a.expiration_date
                WITH auth, a
                MATCH (cl:Client {id: a.client_id})
                MATCH (s:Service {name: a.service_type})
                MERGE (cl)-[:CLIENT_HAS_AUTHORIZATION]->(auth)
                MERGE (auth)-[:AUTHORIZATION_FOR_SERVICE]->(s)
                """,
                rows=batch,
            )

        print(f"Loading {len(data['appointments'])} Appointment nodes...")
        for batch in chunked(data["appointments"], 500):
            session.run(
                """
                UNWIND $rows AS a
                MERGE (appt:Appointment {id: a.id})
                SET appt.datetime = toString(a.appointment_datetime), appt.status = a.status
                WITH appt, a
                MATCH (cl:Client {id: a.client_id})
                MATCH (prov:Provider {name: a.provider})
                MERGE (cl)-[:CLIENT_HAS_APPOINTMENT]->(appt)
                MERGE (appt)-[:APPOINTMENT_WITH_PROVIDER]->(prov)
                WITH appt, a
                WHERE a.authorization_id IS NOT NULL
                MATCH (auth:Authorization {id: a.authorization_id})
                MERGE (appt)-[:APPOINTMENT_REQUIRES_AUTHORIZATION]->(auth)
                """,
                rows=batch,
            )

        print("Computing risk factors (same conditions used for alerts)...")
        pools = compute_risk_pools(
            data["clients"], data["eligibility_checks"], data["authorizations"], data["appointments"], data["tasks"]
        )
        pools["multiple_unresolved_issues"] = compute_multiple_issues_pool(pools)
        for risk_type, candidates in pools.items():
            client_ids = sorted({c["client_id"] for c in candidates})
            session.run("MERGE (:RiskFactor {name: $name})", name=risk_type)
            for batch in chunked(client_ids, 1000):
                session.run(
                    """
                    UNWIND $ids AS cid
                    MATCH (cl:Client {id: cid})
                    MATCH (rf:RiskFactor {name: $risk_type})
                    MERGE (cl)-[:CLIENT_HAS_RISK_FACTOR]->(rf)
                    """,
                    ids=batch,
                    risk_type=risk_type,
                )
            print(f"  {risk_type}: {len(client_ids)} clients")

        counts = session.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY label"
        ).data()
        print("\n--- Graph node counts ---")
        for row in counts:
            print(f"  {row['label']}: {row['n']}")

    driver.close()
    print("\nNeo4j seed complete.")


if __name__ == "__main__":
    main()
