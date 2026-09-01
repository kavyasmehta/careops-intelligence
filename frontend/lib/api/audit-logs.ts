import { apiFetch, buildQuery, type ListResponse } from "@/lib/api";
import type { AuditLog } from "@/types/entities";

export async function listAuditLogs(params: { entity_type?: string; entity_id?: string; page?: number; page_size?: number }) {
  return apiFetch<ListResponse<AuditLog>>(`/api/v1/audit-logs${buildQuery(params)}`);
}
