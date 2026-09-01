import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { Authorization, AuthorizationStatus } from "@/types/entities";

export interface ListAuthorizationsParams {
  page?: number;
  page_size?: number;
  sort?: string;
  client_id?: string;
  status?: AuthorizationStatus | "";
}

export async function listAuthorizations(params: ListAuthorizationsParams = {}): Promise<ListResponse<Authorization>> {
  return apiFetch<ListResponse<Authorization>>(`/api/v1/authorizations${buildQuery(params)}`);
}

export async function listExpiringAuthorizations(withinDays = 14): Promise<ListResponse<Authorization>> {
  return apiFetch<ListResponse<Authorization>>(`/api/v1/authorizations/expiring?within_days=${withinDays}`);
}

export interface AuthorizationInput {
  client_id: string;
  payer: string;
  authorization_number: string;
  service_type: string;
  units_approved: number;
  units_used: number;
  effective_date: string;
  expiration_date: string;
  status: AuthorizationStatus;
}

export async function createAuthorization(input: AuthorizationInput): Promise<ItemResponse<Authorization>> {
  return apiFetch<ItemResponse<Authorization>>("/api/v1/authorizations", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function updateAuthorization(
  id: string,
  input: Partial<Pick<AuthorizationInput, "units_used" | "status" | "expiration_date">>,
): Promise<ItemResponse<Authorization>> {
  return apiFetch<ItemResponse<Authorization>>(`/api/v1/authorizations/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}
