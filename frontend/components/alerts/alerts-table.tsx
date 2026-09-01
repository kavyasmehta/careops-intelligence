"use client";

import type { ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { useMemo } from "react";

import { AssignAlertSelect } from "@/components/alerts/assign-select";
import { ResolveAlertDialog } from "@/components/alerts/resolve-alert-dialog";
import { DataTable } from "@/components/data-table";
import { FilterSelect } from "@/components/filter-select";
import { AlertStatusBadge, SeverityBadge } from "@/components/status-badge";
import { useClientsLookup, useUsersLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { listAlerts, type ListAlertsParams } from "@/lib/api/alerts";
import { titleCase } from "@/lib/format";
import type { Alert, AlertSeverity, AlertStatus } from "@/types/entities";

const SEVERITY_OPTIONS: AlertSeverity[] = ["critical", "high", "medium", "low"];
const STATUS_OPTIONS: AlertStatus[] = ["open", "in_progress", "resolved"];

export function AlertsTable({ pageSize = 15 }: { pageSize?: number }) {
  const { clientsById } = useClientsLookup();
  const { users, usersById } = useUsersLookup();

  const { data, total, page, setPage, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    Alert,
    ListAlertsParams
  >(listAlerts, { sort: "-severity" }, pageSize);

  const columns = useMemo<ColumnDef<Alert, unknown>[]>(
    () => [
      {
        header: "Client",
        accessorKey: "client_id",
        cell: ({ row }) => {
          const c = clientsById.get(row.original.client_id);
          return c ? (
            <Link href={`/clients/${c.id}`} className="font-medium hover:underline">
              {c.first_name} {c.last_name}
            </Link>
          ) : (
            "—"
          );
        },
      },
      {
        header: "Issue",
        accessorKey: "alert_type",
        cell: ({ row }) => (
          <div className="max-w-xs">
            <p className="text-sm font-medium">{titleCase(row.original.alert_type)}</p>
            <p className="text-xs text-muted-foreground">{row.original.explanation}</p>
          </div>
        ),
      },
      { header: "Severity", accessorKey: "severity", cell: ({ row }) => <SeverityBadge value={row.original.severity} /> },
      {
        header: "Recommended action",
        accessorKey: "recommended_action",
        cell: ({ row }) => <span className="max-w-xs text-sm text-muted-foreground">{row.original.recommended_action}</span>,
      },
      {
        header: "Owner",
        accessorKey: "assigned_employee_id",
        cell: ({ row }) =>
          row.original.status === "resolved" ? (
            (row.original.assigned_employee_id && usersById.get(row.original.assigned_employee_id)?.name) || "—"
          ) : (
            <AssignAlertSelect
              alertId={row.original.id}
              assignedEmployeeId={row.original.assigned_employee_id}
              employees={users}
              onSaved={refetch}
            />
          ),
      },
      { header: "Status", accessorKey: "status", cell: ({ row }) => <AlertStatusBadge value={row.original.status} /> },
      {
        id: "actions",
        header: "",
        cell: ({ row }) =>
          row.original.status !== "resolved" && <ResolveAlertDialog alertId={row.original.id} onSaved={refetch} />,
      },
    ],
    [clientsById, users, usersById, refetch],
  );

  return (
    <DataTable
      columns={columns}
      data={data}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      page={page}
      pageSize={pageSize}
      total={total}
      onPageChange={setPage}
      emptyMessage="No alerts match these filters."
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <FilterSelect
            value={filters.severity ?? ""}
            onChange={(v) => updateFilters({ severity: v as AlertSeverity | "" })}
            allLabel="All severities"
            placeholder="Severity"
            options={SEVERITY_OPTIONS.map((s) => ({ value: s, label: s }))}
          />
          <FilterSelect
            value={filters.status ?? ""}
            onChange={(v) => updateFilters({ status: v as AlertStatus | "" })}
            allLabel="All statuses"
            placeholder="Status"
            options={STATUS_OPTIONS.map((s) => ({ value: s, label: s }))}
          />
        </div>
      }
    />
  );
}
