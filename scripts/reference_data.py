"""Fixed reference data for the synthetic dataset.

These are plain constants rather than their own MongoDB collections —
matching the approved data model, where payers/providers/teams are
denormalized string fields on the documents that reference them, and
exist as first-class nodes only in the Neo4j graph (built from the
distinct values actually used in Mongo — see seed_neo4j.py).

Kept fixed (not Faker-generated) so the "uneven employee workload" and
team assignments are deliberate and reproducible run to run.
"""

PAYERS = [
    "Aetna",
    "UnitedHealthcare",
    "Cigna",
    "Molina Healthcare",
    "Anthem Blue Cross",
]

PROVIDERS = [
    {"name": "Dr. Elena Ruiz", "specialty": "Physical Therapy"},
    {"name": "Dr. Marcus Chen", "specialty": "Occupational Therapy"},
    {"name": "Dr. Priya Nair", "specialty": "Speech Therapy"},
    {"name": "Dr. Samuel Okafor", "specialty": "Behavioral Health"},
    {"name": "Dr. Laura Bianchi", "specialty": "Behavioral Health"},
    {"name": "Dr. James Whitfield", "specialty": "Skilled Nursing"},
    {"name": "Dr. Ana Souza", "specialty": "Skilled Nursing"},
    {"name": "Dr. Michael Osei", "specialty": "Case Management"},
    {"name": "Dr. Rachel Kim", "specialty": "Nutrition Counseling"},
    {"name": "Dr. David Novak", "specialty": "Home Health Aide"},
    {"name": "Dr. Fatima Haidari", "specialty": "Home Health Aide"},
    {"name": "Dr. Robert Tan", "specialty": "Physical Therapy"},
    {"name": "Dr. Grace Adeyemi", "specialty": "Occupational Therapy"},
    {"name": "Dr. Ethan Brooks", "specialty": "Speech Therapy"},
    {"name": "Dr. Nadia Petrova", "specialty": "Case Management"},
]

SERVICE_TYPES = sorted({p["specialty"] for p in PROVIDERS})

TEAMS = [
    "Intake North",
    "Intake South",
    "Authorizations East",
    "Authorizations West",
    "Care Coordination A",
    "Care Coordination B",
]

# 10 employees across the 3 roles and 6 teams. Client-load weights are
# deliberately uneven (see seed_mongo.py) to produce the "uneven
# employee workload" scenario called for in the spec.
EMPLOYEES = [
    {"name": "Dana Whitfield", "role": "operations_manager", "team": "Care Coordination A"},
    {"name": "Priya Anand", "role": "intake_specialist", "team": "Intake North"},
    {"name": "Marcus Lee", "role": "intake_specialist", "team": "Intake North"},
    {"name": "Sofia Herrera", "role": "intake_specialist", "team": "Intake South"},
    {"name": "Jordan Blake", "role": "intake_specialist", "team": "Intake South"},
    {"name": "Wanda Price", "role": "authorization_specialist", "team": "Authorizations East"},
    {"name": "Tom Baptiste", "role": "authorization_specialist", "team": "Authorizations East"},
    {"name": "Ken Ito", "role": "authorization_specialist", "team": "Authorizations West"},
    {"name": "Layla Hassan", "role": "authorization_specialist", "team": "Authorizations West"},
    {"name": "Chris Dubois", "role": "operations_manager", "team": "Care Coordination B"},
]
