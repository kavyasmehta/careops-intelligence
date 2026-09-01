"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { AlertTriangle } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AuthorizationFormDialog } from "@/components/authorizations/authorization-form-dialog";
import { DataTable } from "@/components/data-table";
import { AuthorizationStatusBadge } from "@/components/status-badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useClientsLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { listAuthorizations, listExpiringAuthorizations, type ListAuthorizationsParams } from "@/lib/api/authorizations";
import { formatDate } from "@/lib/format";
import type { Authorization, AuthorizationStatus } from "@/types/entities";

const STATUS_OPTIONS: AuthorizationStatus[] = ["pending", "active", "expired", "exhausted", "denied"];

export default function AuthorizationTrackerPage() {
  const { clientsById } = useClientsLookup();
  const clients = useMemo(() => Array.from(clientsById.values()), [clientsById]);
  const [expiringSoonCount, setExpiringSoonCount] = useState<number | null>(null);

  useEffect(() => {
    listExpiringAuthorizations(14).then((res) => setExpiringSoonCount(res.meta.total));
  }, []);

  const { data, total, page, setPage, pageSize, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    Authorization,
    ListAuthorizationsParams
  >(listAuthorizations, {}, 15);

  const columns = useMemo<ColumnDef<Authorization, unknown>[]>(
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
      { header: "Number", accessorKey: "authorization_number" },
      { header: "Payer", accessorKey: "payer" },
      { header: "Service", accessorKey: "service_type" },
      {
        header: "Units",
        accessorKey: "units_used",
        cell: ({ row }) => {
          const { units_used, units_approved } = row.original;
          const pct = units_approved ? Math.min(100, Math.round((units_used / units_approved) * 100)) : 0;
          return (
            <div className="w-28">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>
                  {units_used}/{units_approved}
                </span>
                <span>{pct}%</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted">
                <div
                  className={`h-1.5 rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-emerald-500"}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        },
      },
      { header: "Expires", accessorKey: "expiration_date", cell: ({ row }) => formatDate(row.original.expiration_date) },
      {
        header: "Status",
        accessorKey: "status",
        cell: ({ row }) => <AuthorizationStatusBadge value={row.original.status} />,
      },
    ],
    [clientsById],
  );

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Authorization Tracker</h1>
          <p className="text-sm text-muted-foreground">{total} authorizations match current filters</p>
        </div>
        <AuthorizationFormDialog clients={clients} onSaved={refetch} />
      </div>

      {expiringSoonCount !== null && expiringSoonCount > 0 && (
        <Card className="border-amber-300 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30">
          <CardContent className="flex items-center gap-2 py-3 text-sm text-amber-900 dark:text-amber-200">
            <AlertTriangle className="size-4" />
            {expiringSoonCount} authorization{expiringSoonCount === 1 ? "" : "s"} expiring within 14 days
          </CardContent>
        </Card>
      )}

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
        emptyMessage="No authorizations match these filters."
        toolbar={
          <Select
            value={filters.status || "all"}
            onValueChange={(value) => updateFilters({ status: !value || value === "all" ? "" : (value as AuthorizationStatus) })}
          >
            <SelectTrigger className="w-48">
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
        }
      />
    </div>
  );
}
