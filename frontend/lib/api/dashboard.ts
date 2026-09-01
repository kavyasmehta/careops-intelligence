import { apiFetch, buildQuery, type ItemResponse } from "@/lib/api";
import type { DashboardMetrics } from "@/types/entities";

export interface DashboardFilters {
  team_id?: string;
  payer?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

export async function getDashboardMetrics(filters: DashboardFilters = {}): Promise<ItemResponse<DashboardMetrics>> {
  return apiFetch<ItemResponse<DashboardMetrics>>(`/api/v1/dashboard/metrics${buildQuery(filters)}`);
}
