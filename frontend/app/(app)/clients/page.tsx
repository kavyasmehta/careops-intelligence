"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Pencil, Search } from "lucide-react";
import Link from "next/link";
import { useMemo } from "react";

import { ClientFormDialog } from "@/components/clients/client-form-dialog";
import { DataTable } from "@/components/data-table";
import { ClientStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useUsersLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { listClients, type ListClientsParams } from "@/lib/api/clients";
import { formatDate } from "@/lib/format";
import type { Client } from "@/types/entities";

const STATUS_FILTERS = ["", "active", "pending", "inactive", "discharged"] as const;

export default function ClientsPage() {
  const { users, usersById } = useUsersLookup();
  const teams = useMemo(() => Array.from(new Set(users.map((u) => u.team_id).filter(Boolean))) as string[], [users]);

  const { data, total, page, setPage, pageSize, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    Client,
    ListClientsParams
  >(listClients, {}, 15);

  const columns = useMemo<ColumnDef<Client, unknown>[]>(
    () => [
      {
        header: "Name",
        accessorKey: "last_name",
        cell: ({ row }) => (
          <Link href={`/clients/${row.original.id}`} className="font-medium hover:underline">
            {row.original.first_name} {row.original.last_name}
          </Link>
        ),
      },
      { header: "Member ID", accessorKey: "member_id" },
      {
        header: "Status",
        accessorKey: "status",
        cell: ({ row }) => <ClientStatusBadge value={row.original.status} />,
      },
      { header: "Team", accessorKey: "assigned_team_id", cell: ({ row }) => row.original.assigned_team_id ?? "—" },
      {
        header: "Assigned to",
        accessorKey: "assigned_employee_id",
        cell: ({ row }) =>
          row.original.assigned_employee_id ? usersById.get(row.original.assigned_employee_id)?.name ?? "—" : "—",
      },
      {
        header: "Created",
        accessorKey: "created_at",
        cell: ({ row }) => formatDate(row.original.created_at),
      },
      {
        id: "actions",
        header: "",
        cell: ({ row }) => (
          <ClientFormDialog
            client={row.original}
            employees={users}
            teams={teams}
            triggerElement={<Button variant="ghost" size="icon" />}
            triggerContent={<Pencil className="size-4" />}
            onSaved={refetch}
          />
        ),
      },
    ],
    [usersById, users, teams, refetch],
  );

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Client Directory</h1>
          <p className="text-sm text-muted-foreground">{total} clients</p>
        </div>
        <ClientFormDialog employees={users} teams={teams} onSaved={refetch} />
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
        emptyMessage="No clients match these filters."
        toolbar={
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
              <Input
                placeholder="Search by name..."
                className="pl-8"
                defaultValue={filters.q ?? ""}
                onChange={(e) => updateFilters({ q: e.target.value })}
              />
            </div>
            <Select
              value={filters.status || "all"}
              onValueChange={(value) => updateFilters({ status: !value || value === "all" ? "" : (value as Client["status"]) })}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUS_FILTERS.filter(Boolean).map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={filters.team_id || "all"}
              onValueChange={(value) => updateFilters({ team_id: !value || value === "all" ? "" : value })}
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All teams</SelectItem>
                {teams.map((team) => (
                  <SelectItem key={team} value={team}>
                    {team}
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
