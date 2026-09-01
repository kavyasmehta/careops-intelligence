"""
Named, documented Cypher queries answering the 5 business questions from
the architecture doc's Neo4j model. Kept separate from the service layer
so the actual graph logic is easy to review/audit on its own.
"""

APPOINTMENTS_WITHOUT_AUTHORIZATION = """
MATCH (c:Client)-[:CLIENT_HAS_APPOINTMENT]->(a:Appointment)
WHERE a.status = 'scheduled'
  AND datetime(a.datetime) > datetime()
  AND NOT EXISTS {
    (a)-[:APPOINTMENT_REQUIRES_AUTHORIZATION]->(:Authorization {status: 'active'})
  }
RETURN c.id AS client_id, c.name AS client_name, a.id AS appointment_id,
       a.datetime AS appointment_datetime
ORDER BY a.datetime ASC
LIMIT $limit
"""

PROVIDERS_WITH_UNRESOLVED_AUTHORIZATIONS = """
MATCH (auth:Authorization)<-[:APPOINTMENT_REQUIRES_AUTHORIZATION]-(appt:Appointment)
      -[:APPOINTMENT_WITH_PROVIDER]->(p:Provider)
WHERE auth.status IN ['expired', 'exhausted']
RETURN p.name AS provider_name, p.specialty AS specialty,
       count(DISTINCT auth) AS unresolved_cases
ORDER BY unresolved_cases DESC
LIMIT $limit
"""

# Payer failure rate is a hybrid query, by design: "failed" is a fact about
# an eligibility_checks document (Mongo's source-of-truth field), while
# "how many clients does this payer cover in total" is answered from the
# graph's CLIENT_COVERED_BY_PAYER edges. Neither store alone answers the
# actual question (a *rate*, not just a raw count).
PAYER_TOTAL_COVERED_CLIENTS = """
MATCH (:Payer {name: $payer})<-[:CLIENT_COVERED_BY_PAYER]-(c:Client)
RETURN count(DISTINCT c) AS total_covered
"""

EMPLOYEE_RISK_WORKLOAD = """
MATCH (e:Employee)<-[:CLIENT_ASSIGNED_TO_EMPLOYEE]-(c:Client)-[:CLIENT_HAS_RISK_FACTOR]->(rf:RiskFactor)
RETURN e.id AS employee_id, e.name AS employee_name, e.role AS role,
       count(rf) AS risk_count
ORDER BY risk_count DESC
LIMIT $limit
"""

SIMILAR_CLIENTS_BY_RISK_FACTOR = """
MATCH (c1:Client {id: $client_id})-[:CLIENT_HAS_RISK_FACTOR]->(rf:RiskFactor)
      <-[:CLIENT_HAS_RISK_FACTOR]-(c2:Client)
WHERE c1 <> c2
WITH c2, collect(rf.name) AS shared_risk_factors, count(rf) AS shared_count
RETURN c2.id AS client_id, c2.name AS client_name, shared_risk_factors, shared_count
ORDER BY shared_count DESC
LIMIT $limit
"""

# --- Ego network (Network Intelligence page) ---
# Three focused queries rather than one sprawling MATCH: keeps each result
# small and bounded (recent-N, not all-time) so the resulting graph stays
# readable, per the "avoid an unreadable graph with every node" requirement.

EGO_CORE = """
MATCH (c:Client {id: $client_id})
OPTIONAL MATCH (c)-[:CLIENT_ASSIGNED_TO_EMPLOYEE]->(emp:Employee)
OPTIONAL MATCH (c)-[:CLIENT_COVERED_BY_PAYER]->(payer:Payer)
OPTIONAL MATCH (c)-[:CLIENT_HAS_RISK_FACTOR]->(rf:RiskFactor)
RETURN c.id AS client_id, c.name AS client_name,
       emp.id AS employee_id, emp.name AS employee_name,
       collect(DISTINCT payer.name) AS payers,
       collect(DISTINCT rf.name) AS risk_factors
"""

EGO_RECENT_APPOINTMENTS = """
MATCH (c:Client {id: $client_id})-[:CLIENT_HAS_APPOINTMENT]->(a:Appointment)
OPTIONAL MATCH (a)-[:APPOINTMENT_WITH_PROVIDER]->(p:Provider)
RETURN a.id AS appointment_id, a.datetime AS appointment_datetime, a.status AS status,
       p.name AS provider_name
ORDER BY a.datetime DESC
LIMIT $limit
"""

EGO_RECENT_AUTHORIZATIONS = """
MATCH (c:Client {id: $client_id})-[:CLIENT_HAS_AUTHORIZATION]->(auth:Authorization)
OPTIONAL MATCH (auth)-[:AUTHORIZATION_FOR_SERVICE]->(s:Service)
RETURN auth.id AS authorization_id, auth.authorization_number AS authorization_number,
       auth.status AS status, s.name AS service_name
ORDER BY auth.expiration_date DESC
LIMIT $limit
"""
