import type { DemoRole } from "@/lib/demo-session";

export interface User {
  id: string;
  name: string;
  role: DemoRole;
  team_id: string | null;
  created_at: string;
  updated_at: string;
}

export type ClientStatus = "active" | "pending" | "inactive" | "discharged";

export interface Address {
  line1: string;
  city: string;
  state: string;
  zip: string;
}

export interface Client {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  member_id: string;
  email: string | null;
  phone: string | null;
  address: Address | null;
  assigned_team_id: string | null;
  assigned_employee_id: string | null;
  status: ClientStatus;
  created_at: string;
  updated_at: string;
}

export type CoverageStatus = "active" | "inactive" | "failed" | "pending";

export interface EligibilityCheck {
  id: string;
  client_id: string;
  payer: string;
  check_date: string;
  coverage_status: CoverageStatus;
  effective_date: string | null;
  termination_date: string | null;
  plan_name: string | null;
  failure_reason: string | null;
  source: string;
  processed: boolean;
  created_at: string;
  updated_at: string;
}

export type AuthorizationStatus = "pending" | "active" | "expired" | "exhausted" | "denied";

export interface Authorization {
  id: string;
  client_id: string;
  payer: string;
  authorization_number: string;
  service_type: string;
  units_approved: number;
  units_used: number;
  effective_date: string;
  expiration_date: string;
  status: AuthorizationStatus;
  created_at: string;
  updated_at: string;
}

export type AppointmentStatus = "scheduled" | "completed" | "cancelled" | "no_show";

export interface Appointment {
  id: string;
  client_id: string;
  appointment_datetime: string;
  service_type: string;
  provider: string;
  location: string;
  status: AppointmentStatus;
  authorization_id: string | null;
  created_at: string;
  updated_at: string;
}

export type AlertType =
  | "appointment_without_authorization"
  | "authorization_expiring"
  | "authorization_units_exhausted"
  | "eligibility_failed"
  | "coverage_ending_soon"
  | "overdue_task"
  | "multiple_unresolved_issues";

export type AlertSeverity = "low" | "medium" | "high" | "critical";
export type AlertStatus = "open" | "in_progress" | "resolved";

export interface Alert {
  id: string;
  client_id: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  explanation: string;
  recommended_action: string;
  assigned_employee_id: string | null;
  status: AlertStatus;
  resolution_notes: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export type TaskPriority = "low" | "medium" | "high" | "urgent";
export type TaskStatus = "open" | "in_progress" | "completed";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  client_id: string | null;
  assigned_employee_id: string;
  priority: TaskPriority;
  due_date: string;
  status: TaskStatus;
  is_overdue: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseNote {
  id: string;
  client_id: string;
  author: string;
  note_text: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  user: string;
  action: string;
  entity_type: string;
  entity_id: string;
  timestamp: string;
  previous_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
}

export interface StatusCount {
  label: string;
  count: number;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface EmployeeWorkload {
  employee_id: string;
  employee_name: string;
  open_items: number;
}

export interface PayerPerformance {
  payer: string;
  total_checks: number;
  success_rate: number;
}

export interface DashboardMetrics {
  active_clients: number;
  eligibility_success_rate: number;
  upcoming_appointments: number;
  expiring_authorizations: number;
  open_high_priority_alerts: number;
  avg_resolution_time_hours: number | null;
  cases_by_status: StatusCount[];
  eligibility_trend: TrendPoint[];
  authorization_expiration_trend: TrendPoint[];
  workload_by_employee: EmployeeWorkload[];
  payer_performance: PayerPerformance[];
}
