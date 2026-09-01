import { apiFetch, buildQuery, type ItemResponse, type ListResponse } from "@/lib/api";
import type { Appointment, AppointmentStatus } from "@/types/entities";

export interface ListAppointmentsParams {
  page?: number;
  page_size?: number;
  sort?: string;
  client_id?: string;
  status?: AppointmentStatus | "";
  provider?: string;
  service_type?: string;
}

export async function listAppointments(params: ListAppointmentsParams = {}): Promise<ListResponse<Appointment>> {
  return apiFetch<ListResponse<Appointment>>(`/api/v1/appointments${buildQuery(params)}`);
}

export interface AppointmentInput {
  client_id: string;
  appointment_datetime: string;
  service_type: string;
  provider: string;
  location: string;
  status: AppointmentStatus;
  authorization_id?: string | null;
}

export async function createAppointment(input: AppointmentInput): Promise<ItemResponse<Appointment>> {
  return apiFetch<ItemResponse<Appointment>>("/api/v1/appointments", { method: "POST", body: JSON.stringify(input) });
}

export async function updateAppointment(
  id: string,
  input: Partial<Pick<AppointmentInput, "status" | "authorization_id" | "provider" | "location">>,
): Promise<ItemResponse<Appointment>> {
  return apiFetch<ItemResponse<Appointment>>(`/api/v1/appointments/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}
