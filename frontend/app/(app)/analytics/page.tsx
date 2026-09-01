"use client";

import { Download } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api";
import { downloadCsvExport, getAnalyticsOverview, type ExportEntity } from "@/lib/api/analytics";
import { titleCase } from "@/lib/format";
import type { AnalyticsOverview } from "@/types/entities";

const EXPORTS: { entity: ExportEntity; label: string }[] = [
  { entity: "clients", label: "Clients" },
  { entity: "eligibility-checks", label: "Eligibility Checks" },
  { entity: "authorizations", label: "Authorizations" },
  { entity: "appointments", label: "Appointments" },
  { entity: "alerts", label: "Alerts" },
];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    getAnalyticsOverview()
      .then((res) => setOverview(res.data))
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : "Failed to load analytics."));
  };

  // Fetch-on-mount; see hooks/use-paginated-list.ts for why this pattern
  // doesn't trigger the cascading-render case the lint rule targets.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(load, []);

  const handleExport = async (entity: ExportEntity) => {
    try {
      await downloadCsvExport(entity);
      toast.success(`${entity} exported`);
    } catch {
      toast.error("Export failed");
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div>
        <h1 className="text-xl font-semibold">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Operational trends, outcome distributions, and team workload — complements the executive dashboard.
        </p>
      </div>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && !overview && <LoadingState rows={6} />}
      {!error && overview && (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Alerts created (last 12 weeks)</CardTitle>
              </CardHeader>
              <CardContent className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={overview.alerts_created_trend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="week_label" tick={{ fontSize: 10 }} interval={1} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="alerts_created" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Avg. alert resolution time by severity (hours)</CardTitle>
              </CardHeader>
              <CardContent className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={overview.resolution_time_by_severity.map((r) => ({ ...r, severity: titleCase(r.severity) }))}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="severity" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="avg_hours" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Authorization outcomes</CardTitle>
              </CardHeader>
              <CardContent className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={overview.authorization_outcomes.map((o) => ({ ...o, label: titleCase(o.label) }))}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Eligibility outcomes</CardTitle>
              </CardHeader>
              <CardContent className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={overview.eligibility_outcomes.map((o) => ({ ...o, label: titleCase(o.label) }))}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="var(--chart-4)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Team workload</CardTitle>
              </CardHeader>
              <CardContent className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={overview.team_workload}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="team" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="open_alerts" name="Open alerts" fill="var(--chart-5)" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="open_tasks" name="Open tasks" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Top eligibility failure reasons</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {overview.top_failure_reasons.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No failures recorded.</p>
                ) : (
                  overview.top_failure_reasons.map((r) => (
                    <div key={r.reason} className="flex items-center justify-between text-sm">
                      <span>{r.reason}</span>
                      <span className="font-medium tabular-nums">{r.count}</span>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Export filtered data as CSV</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {EXPORTS.map(({ entity, label }) => (
                <Button key={entity} variant="outline" size="sm" onClick={() => handleExport(entity)}>
                  <Download className="size-4" /> {label}
                </Button>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
