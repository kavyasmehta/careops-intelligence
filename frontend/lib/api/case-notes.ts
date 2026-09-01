import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { CaseNote } from "@/types/entities";

export async function listCaseNotes(params: { client_id?: string; page?: number; page_size?: number } = {}) {
  return apiFetch<ListResponse<CaseNote>>(`/api/v1/case-notes${buildQuery(params)}`);
}

export async function createCaseNote(input: {
  client_id: string;
  author: string;
  note_text: string;
  tags: string[];
}): Promise<ItemResponse<CaseNote>> {
  return apiFetch<ItemResponse<CaseNote>>("/api/v1/case-notes", { method: "POST", body: JSON.stringify(input) });
}
