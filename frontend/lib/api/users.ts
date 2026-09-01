import { apiFetch, type ListResponse } from "@/lib/api";
import type { User } from "@/types/entities";

export async function listUsers(): Promise<ListResponse<User>> {
  return apiFetch<ListResponse<User>>("/api/v1/users");
}
