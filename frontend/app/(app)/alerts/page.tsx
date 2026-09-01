import { AlertsTable } from "@/components/alerts/alerts-table";

export default function AlertCenterPage() {
  return (
    <div className="flex flex-1 flex-col gap-4">
      <div>
        <h1 className="text-xl font-semibold">Alert Center</h1>
        <p className="text-sm text-muted-foreground">
          Severity-ranked operational alerts with assignment and resolution workflow.
        </p>
      </div>
      <AlertsTable />
    </div>
  );
}
