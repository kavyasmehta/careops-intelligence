import { AlertsTable } from "@/components/alerts/alerts-table";
import { TasksTable } from "@/components/tasks/tasks-table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

/**
 * The spec's work-queue table (Client/Issue/Severity/Recommended action/
 * Owner/Due date/Status) doesn't map onto a single backend entity —
 * "Issue"+"Severity"+"Recommended action" are Alert fields, "Due date"
 * is a Task field. Rather than inventing a fake merged schema, this
 * page presents both real, fully-functional queues side by side as tabs.
 */
export default function WorkQueuePage() {
  return (
    <div className="flex flex-1 flex-col gap-4">
      <div>
        <h1 className="text-xl font-semibold">Operations Work Queue</h1>
        <p className="text-sm text-muted-foreground">Everything currently open across alerts and tasks.</p>
      </div>
      <Tabs defaultValue="alerts">
        <TabsList>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
        </TabsList>
        <TabsContent value="alerts">
          <AlertsTable />
        </TabsContent>
        <TabsContent value="tasks">
          <TasksTable />
        </TabsContent>
      </Tabs>
    </div>
  );
}
