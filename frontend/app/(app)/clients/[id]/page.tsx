"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import {
  AlertStatusBadge,
  AppointmentStatusBadge,
  AuthorizationStatusBadge,
  ClientStatusBadge,
  CoverageStatusBadge,
  SeverityBadge,
  TaskStatusBadge,
} from "@/components/status-badge";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { EmptyState } from "@/components/states/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useClientProfile } from "@/hooks/use-client-profile";
import { useDemoSession } from "@/contexts/demo-session-context";
import { ApiError } from "@/lib/api";
import { createCaseNote } from "@/lib/api/case-notes";
import { formatDate, formatDateTime } from "@/lib/format";

export default function ClientProfilePage() {
  const params = useParams<{ id: string }>();
  const clientId = params.id;
  const { client, eligibility, authorizations, appointments, alerts, tasks, notes, auditLogs, isLoading, error, refetch } =
    useClientProfile(clientId);
  const { session } = useDemoSession();
  const [noteText, setNoteText] = useState("");
  const [submittingNote, setSubmittingNote] = useState(false);

  if (isLoading) return <LoadingState rows={6} />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!client) return <EmptyState title="Client not found" />;

  const submitNote = async () => {
    if (!noteText.trim()) return;
    setSubmittingNote(true);
    try {
      await createCaseNote({
        client_id: clientId,
        author: session?.name ?? "Demo User",
        note_text: noteText.trim(),
        tags: [],
      });
      setNoteText("");
      toast.success("Note added");
      refetch();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to add note");
    } finally {
      setSubmittingNote(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">
            {client.first_name} {client.last_name}
          </h1>
          <p className="text-sm text-muted-foreground">
            Member ID {client.member_id} · DOB {formatDate(client.date_of_birth)}
          </p>
        </div>
        <ClientStatusBadge value={client.status} />
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="eligibility">Eligibility ({eligibility.length})</TabsTrigger>
          <TabsTrigger value="authorizations">Authorizations ({authorizations.length})</TabsTrigger>
          <TabsTrigger value="appointments">Appointments ({appointments.length})</TabsTrigger>
          <TabsTrigger value="alerts">Alerts &amp; Tasks ({alerts.length + tasks.length})</TabsTrigger>
          <TabsTrigger value="notes">Notes ({notes.length})</TabsTrigger>
          <TabsTrigger value="audit">Audit</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Contact</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              <p>{client.email ?? "No email on file"}</p>
              <p>{client.phone ?? "No phone on file"}</p>
              {client.address && (
                <p className="text-muted-foreground">
                  {client.address.line1}, {client.address.city}, {client.address.state} {client.address.zip}
                </p>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Care team</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              <p>Team: {client.assigned_team_id ?? "Unassigned"}</p>
              <p>Assigned employee ID: {client.assigned_employee_id ?? "Unassigned"}</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="eligibility">
          {eligibility.length === 0 ? (
            <EmptyState description="No eligibility checks recorded for this client." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Payer</TableHead>
                  <TableHead>Check date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Plan</TableHead>
                  <TableHead>Failure reason</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {eligibility.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell>{e.payer}</TableCell>
                    <TableCell>{formatDate(e.check_date)}</TableCell>
                    <TableCell>
                      <CoverageStatusBadge value={e.coverage_status} />
                    </TableCell>
                    <TableCell>{e.plan_name ?? "—"}</TableCell>
                    <TableCell className="text-muted-foreground">{e.failure_reason ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        <TabsContent value="authorizations">
          {authorizations.length === 0 ? (
            <EmptyState description="No authorizations recorded for this client." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Number</TableHead>
                  <TableHead>Payer</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Units</TableHead>
                  <TableHead>Expires</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {authorizations.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{a.authorization_number}</TableCell>
                    <TableCell>{a.payer}</TableCell>
                    <TableCell>{a.service_type}</TableCell>
                    <TableCell>
                      {a.units_used}/{a.units_approved}
                    </TableCell>
                    <TableCell>{formatDate(a.expiration_date)}</TableCell>
                    <TableCell>
                      <AuthorizationStatusBadge value={a.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        <TabsContent value="appointments">
          {appointments.length === 0 ? (
            <EmptyState description="No appointments recorded for this client." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date/time</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Authorization</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointments.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{formatDateTime(a.appointment_datetime)}</TableCell>
                    <TableCell>{a.service_type}</TableCell>
                    <TableCell>{a.provider}</TableCell>
                    <TableCell>
                      <AppointmentStatusBadge value={a.status} />
                    </TableCell>
                    <TableCell>
                      {a.authorization_id ? (
                        "Linked"
                      ) : (
                        <Badge variant="destructive">Missing</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <div>
            <h3 className="mb-2 text-sm font-semibold text-muted-foreground">Alerts</h3>
            {alerts.length === 0 ? (
              <EmptyState description="No alerts for this client." />
            ) : (
              <div className="space-y-2">
                {alerts.map((a) => (
                  <Card key={a.id}>
                    <CardContent className="flex items-start justify-between gap-3 py-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <SeverityBadge value={a.severity} />
                          <AlertStatusBadge value={a.status} />
                        </div>
                        <p className="text-sm">{a.explanation}</p>
                        <p className="text-xs text-muted-foreground">{a.recommended_action}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-muted-foreground">Tasks</h3>
            {tasks.length === 0 ? (
              <EmptyState description="No tasks for this client." />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Due</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tasks.map((t) => (
                    <TableRow key={t.id}>
                      <TableCell>{t.title}</TableCell>
                      <TableCell>
                        {formatDate(t.due_date)} {t.is_overdue && <Badge variant="destructive">Overdue</Badge>}
                      </TableCell>
                      <TableCell>
                        <TaskStatusBadge value={t.status} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </TabsContent>

        <TabsContent value="notes" className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Add a case note..."
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitNote()}
            />
            <Button onClick={submitNote} disabled={submittingNote || !noteText.trim()}>
              Add
            </Button>
          </div>
          {notes.length === 0 ? (
            <EmptyState description="No case notes yet." />
          ) : (
            <div className="space-y-2">
              {notes.map((n) => (
                <Card key={n.id}>
                  <CardContent className="py-3">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{n.author}</span>
                      <span>{formatDateTime(n.created_at)}</span>
                    </div>
                    <p className="mt-1 text-sm">{n.note_text}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="audit">
          {auditLogs.length === 0 ? (
            <EmptyState description="No audit history for this client record yet." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>When</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>{formatDateTime(log.timestamp)}</TableCell>
                    <TableCell>{log.user}</TableCell>
                    <TableCell className="capitalize">{log.action}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
