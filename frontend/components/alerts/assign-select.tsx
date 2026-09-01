"use client";

import { toast } from "sonner";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ApiError } from "@/lib/api";
import { updateAlert } from "@/lib/api/alerts";
import type { User } from "@/types/entities";

export function AssignAlertSelect({
  alertId,
  assignedEmployeeId,
  employees,
  onSaved,
}: {
  alertId: string;
  assignedEmployeeId: string | null;
  employees: User[];
  onSaved: () => void;
}) {
  const assign = async (employeeId: string) => {
    try {
      await updateAlert(alertId, { assigned_employee_id: employeeId, status: "in_progress" });
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to assign alert");
    }
  };

  const byId = new Map(employees.map((e) => [e.id, e]));
  // See ClientPicker for why this render-function form is needed: the
  // stored value is an opaque employee id, not the display label.
  const label = (id: string | null) => (id ? byId.get(id)?.name ?? "Unassigned" : "Unassigned");

  return (
    <Select value={assignedEmployeeId ?? undefined} onValueChange={(value) => value && assign(value)}>
      <SelectTrigger className="w-40" size="sm">
        <SelectValue placeholder="Unassigned">{label}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        {employees.map((emp) => (
          <SelectItem key={emp.id} value={emp.id}>
            {emp.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
