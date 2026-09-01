"use client";

import type { ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";

import { DataTable } from "@/components/data-table";
import { FilterSelect } from "@/components/filter-select";
import { PriorityBadge, TaskStatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useClientsLookup, useUsersLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { ApiError } from "@/lib/api";
import { listTasks, updateTask, type ListTasksParams } from "@/lib/api/tasks";
import { formatDate } from "@/lib/format";
import type { Task, TaskStatus } from "@/types/entities";

const STATUS_OPTIONS: TaskStatus[] = ["open", "in_progress", "completed"];

export function TasksTable({ pageSize = 15 }: { pageSize?: number }) {
  const { clientsById } = useClientsLookup();
  const { usersById } = useUsersLookup();

  const { data, total, page, setPage, filters, updateFilters, isLoading, error, refetch } = usePaginatedList<
    Task,
    ListTasksParams
  >(listTasks, { sort: "due_date" }, pageSize);

  const changeStatus = useCallback(
    async (id: string, status: TaskStatus) => {
      try {
        await updateTask(id, { status });
        refetch();
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Failed to update task");
      }
    },
    [refetch],
  );

  const columns = useMemo<ColumnDef<Task, unknown>[]>(
    () => [
      {
        header: "Client",
        accessorKey: "client_id",
        cell: ({ row }) => {
          const c = row.original.client_id ? clientsById.get(row.original.client_id) : null;
          return c ? (
            <Link href={`/clients/${c.id}`} className="font-medium hover:underline">
              {c.first_name} {c.last_name}
            </Link>
          ) : (
            <span className="text-muted-foreground">General</span>
          );
        },
      },
      { header: "Task", accessorKey: "title" },
      { header: "Priority", accessorKey: "priority", cell: ({ row }) => <PriorityBadge value={row.original.priority} /> },
      {
        header: "Due date",
        accessorKey: "due_date",
        cell: ({ row }) => (
          <div className="flex items-center gap-2">
            {formatDate(row.original.due_date)}
            {row.original.is_overdue && <Badge variant="destructive">Overdue</Badge>}
          </div>
        ),
      },
      {
        header: "Owner",
        accessorKey: "assigned_employee_id",
        cell: ({ row }) => usersById.get(row.original.assigned_employee_id)?.name ?? "—",
      },
      {
        header: "Status",
        accessorKey: "status",
        cell: ({ row }) =>
          row.original.status === "completed" ? (
            <TaskStatusBadge value="completed" />
          ) : (
            <Select value={row.original.status} onValueChange={(v) => changeStatus(row.original.id, v as TaskStatus)}>
              <SelectTrigger className="w-36" size="sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUS_OPTIONS.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ),
      },
    ],
    [clientsById, usersById, changeStatus],
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
      emptyMessage="No tasks match these filters."
      toolbar={
        <FilterSelect
          value={filters.status ?? ""}
          onChange={(v) => updateFilters({ status: v as TaskStatus | "" })}
          allLabel="All statuses"
          placeholder="Status"
          options={STATUS_OPTIONS.map((s) => ({ value: s, label: s }))}
        />
      }
    />
  );
}
