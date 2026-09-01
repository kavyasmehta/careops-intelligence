import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { Client, ClientStatus } from "@/types/entities";

export interface ListClientsParams {
  page?: number;
  page_size?: number;
  sort?: string;
  q?: string;
  status?: ClientStatus | "";
  team_id?: string;
  employee_id?: string;
}

export async function listClients(params: ListClientsParams = {}): Promise<ListResponse<Client>> {
  return apiFetch<ListResponse<Client>>(`/api/v1/clients${buildQuery(params)}`);
}

export async function getClient(id: string): Promise<ItemResponse<Client>> {
  return apiFetch<ItemResponse<Client>>(`/api/v1/clients/${id}`);
}

export interface ClientInput {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  member_id: string;
  email?: string | null;
  phone?: string | null;
  address?: Client["address"];
  assigned_team_id?: string | null;
  assigned_employee_id?: string | null;
  status: ClientStatus;
}

export async function createClient(input: ClientInput): Promise<ItemResponse<Client>> {
  return apiFetch<ItemResponse<Client>>("/api/v1/clients", { method: "POST", body: JSON.stringify(input) });
}

export async function updateClient(id: string, input: Partial<ClientInput>): Promise<ItemResponse<Client>> {
  return apiFetch<ItemResponse<Client>>(`/api/v1/clients/${id}`, { method: "PATCH", body: JSON.stringify(input) });
}
