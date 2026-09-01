from pydantic import BaseModel


class RiskFactorDetail(BaseModel):
    code: str
    label: str
    points: int
    detail: str


class RiskScore(BaseModel):
    client_id: str
    score: int
    band: str
    factors: list[RiskFactorDetail]
