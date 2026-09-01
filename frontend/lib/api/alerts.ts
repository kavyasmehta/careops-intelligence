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

export interface AlertGenerationResult {
  scanned_clients: number;
  alerts_created: number;
  alerts_skipped_as_duplicate: number;
  created_by_type: Record<string, number>;
}

export async function runAlertGeneration(): Promise<ItemResponse<AlertGenerationResult>> {
  return apiFetch<ItemResponse<AlertGenerationResult>>("/api/v1/alerts/generate", { method: "POST" });
}

export async function updateAlert(
  id: string,
  input: Partial<{ assigned_employee_id: string | null; status: AlertStatus; resolution_notes: string | null }>,
): Promise<ItemResponse<Alert>> {
  return apiFetch<ItemResponse<Alert>>(`/api/v1/alerts/${id}`, { method: "PATCH", body: JSON.stringify(input) });
}
