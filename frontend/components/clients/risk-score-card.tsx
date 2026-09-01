"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api";
import { getClientRisk, type RiskScore } from "@/lib/api/risk";

const BAND_COLORS: Record<string, string> = {
  Low: "text-emerald-600 dark:text-emerald-400",
  Medium: "text-amber-600 dark:text-amber-400",
  High: "text-orange-600 dark:text-orange-400",
  Critical: "text-red-600 dark:text-red-400",
};

export function RiskScoreCard({ clientId }: { clientId: string }) {
  const [risk, setRisk] = useState<RiskScore | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    getClientRisk(clientId)
      .then((res) => setRisk(res.data))
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : "Failed to load risk score."));
  };

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(load, [clientId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Operational risk score</CardTitle>
      </CardHeader>
      <CardContent>
        {error && <ErrorState message={error} onRetry={load} />}
        {!error && !risk && <LoadingState rows={2} />}
        {risk && (
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <span className={`text-3xl font-bold tabular-nums ${BAND_COLORS[risk.band]}`}>{risk.score}</span>
              <span className={`text-sm font-medium ${BAND_COLORS[risk.band]}`}>{risk.band}</span>
              <span className="text-xs text-muted-foreground">/ 100</span>
            </div>
            {risk.factors.length === 0 ? (
              <EmptyState description="No active risk factors for this client." />
            ) : (
              <ul className="space-y-1.5 text-sm">
                {risk.factors.map((f) => (
                  <li key={f.code} className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium">{f.label}</p>
                      <p className="text-xs text-muted-foreground">{f.detail}</p>
                    </div>
                    <span className="shrink-0 text-xs font-medium text-muted-foreground">+{f.points}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
