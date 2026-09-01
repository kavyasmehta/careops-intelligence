import { apiFetch, type ItemResponse } from "@/lib/api";

export interface RiskFactorDetail {
  code: string;
  label: string;
  points: number;
  detail: string;
}

export interface RiskScore {
  client_id: string;
  score: number;
  band: "Low" | "Medium" | "High" | "Critical";
  factors: RiskFactorDetail[];
}

export interface CaseSummary {
  client_id: string;
  summary: string;
  generated_by: "template" | "llm";
  disclaimer: string;
  generated_at: string;
}

export async function getClientRisk(clientId: string): Promise<ItemResponse<RiskScore>> {
  return apiFetch<ItemResponse<RiskScore>>(`/api/v1/clients/${clientId}/risk`);
}

export async function getClientSummary(clientId: string): Promise<ItemResponse<CaseSummary>> {
  return apiFetch<ItemResponse<CaseSummary>>(`/api/v1/clients/${clientId}/summary`);
}
