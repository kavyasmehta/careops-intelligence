"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import { listAlerts } from "@/lib/api/alerts";
import { listAppointments } from "@/lib/api/appointments";
import { listAuditLogs } from "@/lib/api/audit-logs";
import { listAuthorizations } from "@/lib/api/authorizations";
import { listCaseNotes } from "@/lib/api/case-notes";
import { getClient } from "@/lib/api/clients";
import { listEligibilityChecks } from "@/lib/api/eligibility";
import { listTasks } from "@/lib/api/tasks";
import type {
  Alert,
  Appointment,
  AuditLog,
  Authorization,
  CaseNote,
  Client,
  EligibilityCheck,
  Task,
} from "@/types/entities";

export function useClientProfile(clientId: string) {
  const [client, setClient] = useState<Client | null>(null);
  const [eligibility, setEligibility] = useState<EligibilityCheck[]>([]);
  const [authorizations, setAuthorizations] = useState<Authorization[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setIsLoading(true);
    setError(null);
    Promise.all([
      getClient(clientId),
      listEligibilityChecks({ client_id: clientId, page_size: 50, sort: "-check_date" }),
      listAuthorizations({ client_id: clientId, page_size: 50 }),
      listAppointments({ client_id: clientId, page_size: 50, sort: "-appointment_datetime" }),
      listAlerts({ client_id: clientId, page_size: 50 }),
      listTasks({ client_id: clientId, page_size: 50 }),
      listCaseNotes({ client_id: clientId, page_size: 50 }),
      listAuditLogs({ entity_type: "client", entity_id: clientId, page_size: 50 }),
    ])
      .then(([c, e, a, appt, al, t, n, log]) => {
        setClient(c.data);
        setEligibility(e.data);
        setAuthorizations(a.data);
        setAppointments(appt.data);
        setAlerts(al.data);
        setTasks(t.data);
        setNotes(n.data);
        setAuditLogs(log.data);
      })
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : "Failed to load client."))
      .finally(() => setIsLoading(false));
  }, [clientId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  return { client, eligibility, authorizations, appointments, alerts, tasks, notes, auditLogs, isLoading, error, refetch: load };
}
