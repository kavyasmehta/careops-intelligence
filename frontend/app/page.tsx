"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  data: {
    status: string;
    dependencies: { mongo: boolean; neo4j: boolean };
  };
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse["data"] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => res.json())
      .then((body: HealthResponse) => setHealth(body.data))
      .catch(() => setError("Could not reach the CareOps API."));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-slate-50 p-8 font-sans dark:bg-slate-950">
      <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
        CareOps Intelligence — Infrastructure Check
      </h1>
      <p className="max-w-lg text-center text-sm text-slate-500 dark:text-slate-400">
        Portfolio demonstration using synthetic data. Not intended for clinical use or
        storage of protected health information.
      </p>
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm dark:border-slate-800 dark:bg-slate-900">
        {error && <p className="text-red-600">{error}</p>}
        {!error && !health && <p className="text-slate-500">Checking API health…</p>}
        {health && (
          <ul className="space-y-1">
            <li>
              API status: <strong>{health.status}</strong>
            </li>
            <li>MongoDB: {health.dependencies.mongo ? "✅ connected" : "❌ unreachable"}</li>
            <li>Neo4j: {health.dependencies.neo4j ? "✅ connected" : "❌ unreachable"}</li>
          </ul>
        )}
      </div>
    </div>
  );
}
