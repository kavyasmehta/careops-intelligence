import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { Task, TaskStatus } from "@/types/entities";

export interface ListTasksParams {
  page?: number;
  page_size?: number;
  sort?: string;
  client_id?: string;
  status?: TaskStatus | "";
  assigned_employee_id?: string;
}

export async function listTasks(params: ListTasksParams = {}): Promise<ListResponse<Task>> {
  return apiFetch<ListResponse<Task>>(`/api/v1/tasks${buildQuery(params)}`);
}

export async function updateTask(
  id: string,
  input: Partial<{ status: TaskStatus; priority: Task["priority"]; assigned_employee_id: string; due_date: string }>,
): Promise<ItemResponse<Task>> {
  return apiFetch<ItemResponse<Task>>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(input) });
}
