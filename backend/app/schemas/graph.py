from pydantic import BaseModel


class AppointmentWithoutAuthorization(BaseModel):
    client_id: str
    client_name: str
    appointment_id: str
    appointment_datetime: str


class ProviderUnresolvedCases(BaseModel):
    provider_name: str
    specialty: str | None
    unresolved_cases: int


class PayerFailureRate(BaseModel):
    payer: str
    failed_checks: int
    total_covered_clients: int
    failure_rate: float


class EmployeeRiskWorkload(BaseModel):
    employee_id: str
    employee_name: str
    role: str
    risk_count: int


class SimilarClient(BaseModel):
    client_id: str
    client_name: str
    shared_risk_factors: list[str]
    shared_count: int


class EgoNode(BaseModel):
    id: str
    label: str
    type: str


class EgoEdge(BaseModel):
    source: str
    target: str
    type: str


class ClientEgoNetwork(BaseModel):
    nodes: list[EgoNode]
    edges: list[EgoEdge]
