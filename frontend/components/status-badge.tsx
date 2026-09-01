import { cn } from "@/lib/utils";
import { titleCase } from "@/lib/format";

type Tone = "success" | "warning" | "danger" | "info" | "neutral";

const TONE_CLASSES: Record<Tone, string> = {
  success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300",
  danger: "bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300",
  info: "bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-300",
  neutral: "bg-muted text-muted-foreground",
};

function Badge({ label, tone }: { label: string; tone: Tone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap",
        TONE_CLASSES[tone],
      )}
    >
      {label}
    </span>
  );
}

const CLIENT_STATUS_TONE: Record<string, Tone> = {
  active: "success",
  pending: "warning",
  inactive: "neutral",
  discharged: "neutral",
};

const COVERAGE_STATUS_TONE: Record<string, Tone> = {
  active: "success",
  failed: "danger",
  pending: "warning",
  inactive: "neutral",
};

const AUTHORIZATION_STATUS_TONE: Record<string, Tone> = {
  active: "success",
  pending: "warning",
  expired: "danger",
  exhausted: "danger",
  denied: "danger",
};

const APPOINTMENT_STATUS_TONE: Record<string, Tone> = {
  scheduled: "info",
  completed: "success",
  cancelled: "neutral",
  no_show: "danger",
};

const ALERT_STATUS_TONE: Record<string, Tone> = {
  open: "danger",
  in_progress: "warning",
  resolved: "success",
};

const TASK_STATUS_TONE: Record<string, Tone> = {
  open: "info",
  in_progress: "warning",
  completed: "success",
};

const SEVERITY_TONE: Record<string, Tone> = {
  low: "neutral",
  medium: "info",
  high: "warning",
  critical: "danger",
};

const PRIORITY_TONE: Record<string, Tone> = {
  low: "neutral",
  medium: "info",
  high: "warning",
  urgent: "danger",
};

function makeBadge(map: Record<string, Tone>) {
  return function SpecificBadge({ value }: { value: string }) {
    return <Badge label={titleCase(value)} tone={map[value] ?? "neutral"} />;
  };
}

export const ClientStatusBadge = makeBadge(CLIENT_STATUS_TONE);
export const CoverageStatusBadge = makeBadge(COVERAGE_STATUS_TONE);
export const AuthorizationStatusBadge = makeBadge(AUTHORIZATION_STATUS_TONE);
export const AppointmentStatusBadge = makeBadge(APPOINTMENT_STATUS_TONE);
export const AlertStatusBadge = makeBadge(ALERT_STATUS_TONE);
export const TaskStatusBadge = makeBadge(TASK_STATUS_TONE);
export const SeverityBadge = makeBadge(SEVERITY_TONE);
export const PriorityBadge = makeBadge(PRIORITY_TONE);
