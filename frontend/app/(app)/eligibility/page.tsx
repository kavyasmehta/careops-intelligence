"use client";

import type { ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { useMemo } from "react";

import { DataTable } from "@/components/data-table";
import { RunCheckDialog } from "@/components/eligibility/run-check-dialog";
import { CoverageStatusBadge } from "@/components/status-badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useClientsLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { listEligibilityChecks, type ListEligibilityParams } from "@/lib/api/eligibility";
import { formatDate } from "@/lib/format";
import type { CoverageStatus, EligibilityCheck } from "@/types/entities";

const COVERAGE_OPTIONS: CoverageStatus[] = ["active", "failed", "pending", "inactive"];

export default function EligibilityCenterPage() {
  const { clientsById } = useClientsLookup();
  const clients = useMemo(() => Array.from(clientsById.values()), [clientsById]);

  const { data, total, page, setPage, pageSize, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    EligibilityCheck,
    ListEligibilityParams
  >(listEligibilityChecks, {}, 15);

  const failedCount = useMemo(() => data.filter((d) => d.coverage_status === "failed").length, [data]);

  const columns = useMemo<ColumnDef<EligibilityCheck, unknown>[]>(
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
      { header: "Payer", accessorKey: "payer" },
      { header: "Check date", accessorKey: "check_date", cell: ({ row }) => formatDate(row.original.check_date) },
      {
        header: "Status",
        accessorKey: "coverage_status",
        cell: ({ row }) => <CoverageStatusBadge value={row.original.coverage_status} />,
      },
      { header: "Plan", accessorKey: "plan_name", cell: ({ row }) => row.original.plan_name ?? "—" },
      {
        header: "Failure reason",
        accessorKey: "failure_reason",
        cell: ({ row }) => <span className="text-muted-foreground">{row.original.failure_reason ?? "—"}</span>,
      },
    ],
    [clientsById],
  );

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Eligibility Center</h1>
          <p className="text-sm text-muted-foreground">
            {total} checks match current filters · {failedCount} failed on current page
          </p>
        </div>
        <RunCheckDialog clients={clients} onSaved={refetch} />
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
        emptyMessage="No eligibility checks match these filters."
        toolbar={
          <div className="flex flex-wrap items-center gap-2">
            <Select
              value={filters.coverage_status || "all"}
              onValueChange={(value) =>
                updateFilters({ coverage_status: !value || value === "all" ? "" : (value as CoverageStatus) })
              }
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Coverage status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {COVERAGE_OPTIONS.map((s) => (
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
