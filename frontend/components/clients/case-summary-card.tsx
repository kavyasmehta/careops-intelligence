"use client";

import { Sparkles } from "lucide-react";
import { useState } from "react";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api";
import { getClientSummary, type CaseSummary } from "@/lib/api/risk";

export function CaseSummaryCard({ clientId }: { clientId: string }) {
  const [summary, setSummary] = useState<CaseSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = () => {
    setIsLoading(true);
    setError(null);
    getClientSummary(clientId)
      .then((res) => setSummary(res.data))
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : "Failed to generate summary."))
      .finally(() => setIsLoading(false));
  };

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-sm">Case summary</CardTitle>
        <Button variant="outline" size="sm" onClick={generate} disabled={isLoading}>
          <Sparkles className="size-4" /> {summary ? "Regenerate" : "Generate"}
        </Button>
      </CardHeader>
      <CardContent>
        {error && <ErrorState message={error} onRetry={generate} />}
        {isLoading && <LoadingState rows={2} />}
        {!isLoading && !error && !summary && (
          <p className="text-sm text-muted-foreground">
            Generate a plain-language operational snapshot from this client&apos;s current records.
          </p>
        )}
        {!isLoading && summary && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{summary.generated_by === "llm" ? "AI-generated" : "Auto-generated"}</Badge>
            </div>
            <p className="text-sm">{summary.summary}</p>
            <p className="text-xs italic text-muted-foreground">{summary.disclaimer}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
