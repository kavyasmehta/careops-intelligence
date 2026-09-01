import { apiFetch, type ItemResponse, type ListResponse } from "@/lib/api";
import type {
  AppointmentWithoutAuthorization,
  ClientEgoNetwork,
  EmployeeRiskWorkload,
  PayerFailureRate,
  ProviderUnresolvedCases,
  SimilarClient,
} from "@/types/entities";

export async function getAppointmentsWithoutAuthorization(limit = 20) {
  return apiFetch<ListResponse<AppointmentWithoutAuthorization>>(
    `/api/v1/graph/insights/appointments-without-authorization?limit=${limit}`,
  );
}

export async function getProvidersUnresolvedAuthorizations(limit = 10) {
  return apiFetch<ListResponse<ProviderUnresolvedCases>>(
    `/api/v1/graph/insights/providers-unresolved-authorizations?limit=${limit}`,
  );
}

export async function getPayerFailureRates(limit = 10) {
  return apiFetch<ListResponse<PayerFailureRate>>(`/api/v1/graph/insights/payer-failure-rates?limit=${limit}`);
}

export async function getEmployeeRiskWorkload(limit = 10) {
  return apiFetch<ListResponse<EmployeeRiskWorkload>>(`/api/v1/graph/insights/employee-risk-workload?limit=${limit}`);
}

export async function getSimilarClients(clientId: string, limit = 10) {
  return apiFetch<ListResponse<SimilarClient>>(`/api/v1/graph/insights/similar-clients/${clientId}?limit=${limit}`);
}

export async function getClientEgoNetwork(clientId: string) {
  return apiFetch<ItemResponse<ClientEgoNetwork>>(`/api/v1/graph/clients/${clientId}/ego`);
}
