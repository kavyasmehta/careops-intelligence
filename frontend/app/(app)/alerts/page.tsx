"use client";

import { Zap } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { AlertsTable } from "@/components/alerts/alerts-table";
import { Button } from "@/components/ui/button";
import { useDemoSession } from "@/contexts/demo-session-context";
import { ApiError } from "@/lib/api";
import { runAlertGeneration } from "@/lib/api/alerts";

export default function AlertCenterPage() {
  const { session } = useDemoSession();
  const [isRunning, setIsRunning] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleGenerate = async () => {
    setIsRunning(true);
    try {
      const result = await runAlertGeneration();
      const { alerts_created, scanned_clients } = result.data;
      toast.success(
        alerts_created > 0
          ? `Created ${alerts_created} new alert(s) across ${scanned_clients} clients.`
          : `No new alerts needed — scanned ${scanned_clients} clients, everything is already covered.`,
      );
      setRefreshKey((k) => k + 1);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Alert generation failed.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Alert Center</h1>
          <p className="text-sm text-muted-foreground">
            Severity-ranked operational alerts with assignment and resolution workflow.
          </p>
        </div>
        {session?.role === "operations_manager" && (
          <Button size="sm" onClick={handleGenerate} disabled={isRunning}>
            <Zap className="size-4" /> Run Alert Generation
          </Button>
        )}
      </div>
      <AlertsTable key={refreshKey} />
    </div>
  );
}
