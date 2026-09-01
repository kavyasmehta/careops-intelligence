import { API_BASE_URL, apiFetch, buildQuery, type ItemResponse } from "@/lib/api";
import { getStoredSession } from "@/lib/demo-session";
import type { AnalyticsOverview } from "@/types/entities";

export async function getAnalyticsOverview(): Promise<ItemResponse<AnalyticsOverview>> {
  return apiFetch<ItemResponse<AnalyticsOverview>>("/api/v1/analytics/overview");
}

export type ExportEntity = "clients" | "eligibility-checks" | "authorizations" | "appointments" | "alerts";

/**
 * Triggers a browser download of the CSV. Can't just navigate to the URL
 * (the endpoint requires the X-Demo-Role header, which a plain link click
 * can't set) — fetch with headers, then hand the browser a blob.
 */
export async function downloadCsvExport(entity: ExportEntity, filters: Record<string, string> = {}): Promise<void> {
  const session = getStoredSession();
  const headers = new Headers();
  if (session) {
    headers.set("X-Demo-Role", session.role);
    headers.set("X-Demo-User", session.name);
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/analytics/export/${entity}${buildQuery(filters)}`, { headers });
  if (!response.ok) {
    throw new Error(`Export failed (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${entity}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
