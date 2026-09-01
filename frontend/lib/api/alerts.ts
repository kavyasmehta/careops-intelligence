import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { Alert, AlertSeverity, AlertStatus } from "@/types/entities";

export interface ListAlertsParams {
  page?: number;
  page_size?: number;
  sort?: string;
  client_id?: string;
  status?: AlertStatus | "";
  severity?: AlertSeverity | "";
  assigned_employee_id?: string;
}

export async function listAlerts(params: ListAlertsParams = {}): Promise<ListResponse<Alert>> {
  return apiFetch<ListResponse<Alert>>(`/api/v1/alerts${buildQuery(params)}`);
}

export async function updateAlert(
  id: string,
  input: Partial<{ assigned_employee_id: string | null; status: AlertStatus; resolution_notes: string | null }>,
): Promise<ItemResponse<Alert>> {
  return apiFetch<ItemResponse<Alert>>(`/api/v1/alerts/${id}`, { method: "PATCH", body: JSON.stringify(input) });
}
