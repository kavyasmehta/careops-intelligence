"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { KpiCard } from "@/components/dashboard/kpi-card";
import { FilterSelect } from "@/components/filter-select";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useUsersLookup } from "@/hooks/use-lookups";
import { usePaginatedList } from "@/hooks/use-paginated-list";
import { getDashboardMetrics, type DashboardFilters } from "@/lib/api/dashboard";
import { PAYERS } from "@/lib/constants";
import { titleCase } from "@/lib/format";
import type { DashboardMetrics } from "@/types/entities";

function useDashboardMetrics() {
  // Reuses the paginated-list hook purely for its filter/fetch/loading
  // plumbing; a single metrics object stands in for "data" here.
  const result = usePaginatedList<DashboardMetrics, DashboardFilters>(
    async (params) => {
      const res = await getDashboardMetrics(params);
      return { data: [res.data], meta: { page: 1, page_size: 1, total: 1 } };
    },
    {},
    1,
  );
  return { ...result, metrics: result.data[0] ?? null };
}

export default function DashboardPage() {
  const { users } = useUsersLookup();
  const teams = useMemo(() => Array.from(new Set(users.map((u) => u.team_id).filter(Boolean))) as string[], [users]);
  const { metrics, filters, updateFilters, isLoading, error, refetch } = useDashboardMetrics();

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div>
        <h1 className="text-xl font-semibold">Executive Dashboard</h1>
        <p className="text-sm text-muted-foreground">Operational health across the client population.</p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <FilterSelect
          value={filters.team_id ?? ""}
          onChange={(v) => updateFilters({ team_id: v })}
          allLabel="All teams"
          placeholder="Team"
          className="w-44"
          options={teams.map((t) => ({ value: t, label: t }))}
        />
        <FilterSelect
          value={filters.payer ?? ""}
          onChange={(v) => updateFilters({ payer: v })}
          allLabel="All payers"
          placeholder="Payer"
          className="w-48"
          options={PAYERS.map((p) => ({ value: p, label: p }))}
        />
        {/* Not a generic "all" filter: the backend treats an absent status as
            "active" specifically (see services/dashboard.py), so the empty
            selection is genuinely labeled "Active clients", not "All statuses". */}
        <Select key={filters.status} value={filters.status || "all"} onValueChange={(v) => updateFilters({ status: !v || v === "all" ? "" : v })}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Client status">
              {(v: string | null) =>
                ({ all: "Active clients", pending: "Pending clients", inactive: "Inactive clients", discharged: "Discharged clients" })[
                  v ?? "all"
                ] ?? "Client status"
              }
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Active clients</SelectItem>
            <SelectItem value="pending">Pending clients</SelectItem>
            <SelectItem value="inactive">Inactive clients</SelectItem>
            <SelectItem value="discharged">Discharged clients</SelectItem>
          </SelectContent>
        </Select>
        <Input
          type="date"
          className="w-40"
          value={filters.date_from ?? ""}
          onChange={(e) => updateFilters({ date_from: e.target.value })}
        />
        <span className="text-sm text-muted-foreground">to</span>
        <Input
          type="date"
          className="w-40"
          value={filters.date_to ?? ""}
          onChange={(e) => updateFilters({ date_to: e.target.value })}
        />
      </div>

      {error && <ErrorState message={error} onRetry={refetch} />}
      {!error && isLoading && <LoadingState rows={6} />}
      {!error && !isLoading && metrics && (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            <KpiCard label="Active clients" value={String(metrics.active_clients)} />
            <KpiCard label="Eligibility success rate" value={`${metrics.eligibility_success_rate}%`} />
            <KpiCard label="Upcoming appointments" value={String(metrics.upcoming_appointments)} />
            <KpiCard label="Expiring authorizations" value={String(metrics.expiring_authorizations)} sublabel="within 14 days" />
            <KpiCard label="Open high-priority alerts" value={String(metrics.open_high_priority_alerts)} />
            <KpiCard
              label="Avg. resolution time"
              value={metrics.avg_resolution_time_hours != null ? `${metrics.avg_resolution_time_hours}h` : "—"}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Cases by status</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.cases_by_status.map((s) => ({ ...s, label: titleCase(s.label) }))}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Eligibility check volume</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metrics.eligibility_trend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={4} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="var(--chart-2)" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Authorization expirations (next 8 weeks)</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.authorization_expiration_trend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="value" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Workload by employee (open items)</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.workload_by_employee} layout="vertical" margin={{ left: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis type="number" tick={{ fontSize: 12 }} allowDecimals={false} />
                    <YAxis type="category" dataKey="employee_name" tick={{ fontSize: 11 }} width={100} />
                    <Tooltip />
                    <Bar dataKey="open_items" fill="var(--chart-4)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm">Payer performance (eligibility success rate)</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.payer_performance}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="payer" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 12 }} unit="%" />
                    <Tooltip />
                    <Bar dataKey="success_rate" fill="var(--chart-5)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
