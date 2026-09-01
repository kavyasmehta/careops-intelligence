"use client";

import type { ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { useMemo } from "react";

import { AppointmentFormDialog } from "@/components/appointments/appointment-form-dialog";
import { DataTable } from "@/components/data-table";
import { AppointmentStatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useClientsLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { listAppointments, type ListAppointmentsParams } from "@/lib/api/appointments";
import { SERVICE_TYPES } from "@/lib/constants";
import { formatDateTime } from "@/lib/format";
import type { Appointment, AppointmentStatus } from "@/types/entities";

const STATUS_OPTIONS: AppointmentStatus[] = ["scheduled", "completed", "cancelled", "no_show"];

export default function AppointmentMonitorPage() {
  const { clientsById } = useClientsLookup();
  const clients = useMemo(() => Array.from(clientsById.values()), [clientsById]);

  const { data, total, page, setPage, pageSize, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    Appointment,
    ListAppointmentsParams
  >(listAppointments, {}, 15);

  const columns = useMemo<ColumnDef<Appointment, unknown>[]>(
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
        header: "Date/time",
        accessorKey: "appointment_datetime",
        cell: ({ row }) => formatDateTime(row.original.appointment_datetime),
      },
      { header: "Service", accessorKey: "service_type" },
      { header: "Provider", accessorKey: "provider" },
      { header: "Status", accessorKey: "status", cell: ({ row }) => <AppointmentStatusBadge value={row.original.status} /> },
      {
        header: "Authorization",
        accessorKey: "authorization_id",
        cell: ({ row }) =>
          row.original.authorization_id ? (
            <span className="text-sm text-muted-foreground">Linked</span>
          ) : (
            <Badge variant="destructive">Missing</Badge>
          ),
      },
    ],
    [clientsById],
  );

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Appointment Monitor</h1>
          <p className="text-sm text-muted-foreground">{total} appointments match current filters</p>
        </div>
        <AppointmentFormDialog clients={clients} onSaved={refetch} />
      </div>

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
        emptyMessage="No appointments match these filters."
        toolbar={
          <div className="flex flex-wrap items-center gap-2">
            <Select
              value={filters.status || "all"}
              onValueChange={(value) => updateFilters({ status: !value || value === "all" ? "" : (value as AppointmentStatus) })}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUS_OPTIONS.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={filters.service_type || "all"}
              onValueChange={(value) => updateFilters({ service_type: !value || value === "all" ? "" : value })}
            >
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Service type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All services</SelectItem>
                {SERVICE_TYPES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        }
      />
    </div>
  );
}
