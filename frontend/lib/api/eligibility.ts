import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { CoverageStatus, EligibilityCheck } from "@/types/entities";

export interface ListEligibilityParams {
  page?: number;
  page_size?: number;
  sort?: string;
  client_id?: string;
  coverage_status?: CoverageStatus | "";
}

export async function listEligibilityChecks(params: ListEligibilityParams = {}): Promise<ListResponse<EligibilityCheck>> {
  return apiFetch<ListResponse<EligibilityCheck>>(`/api/v1/eligibility-checks${buildQuery(params)}`);
}

export interface EligibilityCheckInput {
  client_id: string;
  payer: string;
  check_date: string;
  coverage_status: CoverageStatus;
  effective_date?: string | null;
  termination_date?: string | null;
  plan_name?: string | null;
  failure_reason?: string | null;
  source?: string;
  processed?: boolean;
}

export async function createEligibilityCheck(input: EligibilityCheckInput): Promise<ItemResponse<EligibilityCheck>> {
  return apiFetch<ItemResponse<EligibilityCheck>>("/api/v1/eligibility-checks", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
