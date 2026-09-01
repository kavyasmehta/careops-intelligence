"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useEffect, useMemo, useState } from "react";

import { ClientPicker } from "@/components/client-picker";
import { EgoGraph } from "@/components/network/ego-graph";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useClientsLookup } from "@/hooks/use-lookups";
import { ApiError } from "@/lib/api";
import {
  getClientEgoNetwork,
  getEmployeeRiskWorkload,
  getPayerFailureRates,
  getProvidersUnresolvedAuthorizations,
  getSimilarClients,
} from "@/lib/api/graph";
import type {
  ClientEgoNetwork,
  EmployeeRiskWorkload,
  PayerFailureRate,
  ProviderUnresolvedCases,
  SimilarClient,
} from "@/types/entities";

export default function NetworkIntelligencePage() {
  const { clientsById } = useClientsLookup();
  const clients = useMemo(() => Array.from(clientsById.values()), [clientsById]);

  const [payerRates, setPayerRates] = useState<PayerFailureRate[] | null>(null);
  const [employeeWorkload, setEmployeeWorkload] = useState<EmployeeRiskWorkload[] | null>(null);
  const [providers, setProviders] = useState<ProviderUnresolvedCases[] | null>(null);

  useEffect(() => {
    getPayerFailureRates(5).then((res) => setPayerRates(res.data));
    getEmployeeRiskWorkload(5).then((res) => setEmployeeWorkload(res.data));
    getProvidersUnresolvedAuthorizations(5).then((res) => setProviders(res.data));
  }, []);

  const [selectedClientId, setSelectedClientId] = useState("");
  const [ego, setEgo] = useState<ClientEgoNetwork | null>(null);
  const [similar, setSimilar] = useState<SimilarClient[] | null>(null);
  const [egoError, setEgoError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedClientId) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setEgo(null);
    setSimilar(null);
    setEgoError(null);
    getClientEgoNetwork(selectedClientId)
      .then((res) => setEgo(res.data))
      .catch((err: unknown) =>
        setEgoError(err instanceof ApiError ? err.message : "Failed to load this client's network."),
      );
    getSimilarClients(selectedClientId, 5).then((res) => setSimilar(res.data));
  }, [selectedClientId]);

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div>
        <h1 className="text-xl font-semibold">Network Intelligence</h1>
        <p className="text-sm text-muted-foreground">
          Organization-wide graph insights, plus a focused view of any one client&apos;s network.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Payer failure rate</CardTitle>
          </CardHeader>
          <CardContent className="h-48">
            {payerRates ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={payerRates}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="payer" tick={{ fontSize: 9 }} />
                  <YAxis tick={{ fontSize: 11 }} unit="%" />
                  <Tooltip />
                  <Bar dataKey="failure_rate" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <LoadingState rows={3} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Employee risk workload</CardTitle>
          </CardHeader>
          <CardContent className="h-48">
            {employeeWorkload ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={employeeWorkload} layout="vertical" margin={{ left: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="employee_name" tick={{ fontSize: 10 }} width={90} />
                  <Tooltip />
                  <Bar dataKey="risk_count" fill="var(--chart-2)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <LoadingState rows={3} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Providers with unresolved cases</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {providers ? (
              providers.length === 0 ? (
                <p className="text-sm text-muted-foreground">None currently.</p>
              ) : (
                providers.map((p) => (
                  <div key={p.provider_name} className="flex items-center justify-between text-sm">
                    <span>
                      {p.provider_name}
                      <span className="text-muted-foreground"> · {p.specialty}</span>
                    </span>
                    <span className="font-medium tabular-nums">{p.unresolved_cases}</span>
                  </div>
                ))
              )
            ) : (
              <LoadingState rows={3} />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Client network explorer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="max-w-md">
            <ClientPicker clients={clients} value={selectedClientId} onChange={setSelectedClientId} />
          </div>

          {!selectedClientId && <EmptyState description="Pick a client to view their focused relationship network." />}
          {selectedClientId && egoError && <ErrorState message={egoError} />}
          {selectedClientId && !egoError && !ego && <LoadingState rows={4} />}
          {ego && (
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <EgoGraph network={ego} />
              </div>
              <div>
                <h3 className="mb-2 text-sm font-semibold text-muted-foreground">Clients with similar risk patterns</h3>
                {!similar ? (
                  <LoadingState rows={3} />
                ) : similar.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No clients currently share risk factors with this one.</p>
                ) : (
                  <div className="space-y-2">
                    {similar.map((s) => (
                      <button
                        key={s.client_id}
                        onClick={() => setSelectedClientId(s.client_id)}
                        className="w-full rounded-md border px-3 py-2 text-left text-sm hover:border-primary hover:bg-accent"
                      >
                        <div className="font-medium">{s.client_name}</div>
                        <div className="text-xs text-muted-foreground">
                          Shares {s.shared_count} risk factor{s.shared_count === 1 ? "" : "s"}:{" "}
                          {s.shared_risk_factors.join(", ").replace(/_/g, " ")}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
