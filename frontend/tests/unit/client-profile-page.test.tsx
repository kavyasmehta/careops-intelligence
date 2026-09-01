import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DemoSessionProvider } from "@/contexts/demo-session-context";
import type { Client } from "@/types/entities";

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "client-1" }),
}));

const mockClient: Client = {
  id: "client-1",
  first_name: "Jane",
  last_name: "Doe",
  date_of_birth: "1990-01-01",
  member_id: "MBR-1",
  email: null,
  phone: null,
  address: null,
  assigned_team_id: null,
  assigned_employee_id: null,
  status: "active",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const emptyList = { data: [], meta: { page: 1, page_size: 50, total: 0 } };

vi.mock("@/lib/api/clients", () => ({ getClient: vi.fn() }));
vi.mock("@/lib/api/eligibility", () => ({ listEligibilityChecks: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/lib/api/authorizations", () => ({ listAuthorizations: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/lib/api/appointments", () => ({ listAppointments: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/lib/api/alerts", () => ({ listAlerts: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/lib/api/tasks", () => ({ listTasks: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/lib/api/case-notes", () => ({
  listCaseNotes: vi.fn().mockResolvedValue(emptyList),
  createCaseNote: vi.fn(),
}));
vi.mock("@/lib/api/audit-logs", () => ({ listAuditLogs: vi.fn().mockResolvedValue(emptyList) }));
vi.mock("@/components/clients/risk-score-card", () => ({ RiskScoreCard: () => null }));
vi.mock("@/components/clients/case-summary-card", () => ({ CaseSummaryCard: () => null }));

async function renderPage() {
  const { default: ClientProfilePage } = await import("@/app/(app)/clients/[id]/page");
  return render(
    <DemoSessionProvider>
      <ClientProfilePage />
    </DemoSessionProvider>,
  );
}

describe("Client 360 profile page", () => {
  it("shows a loading state before data arrives", async () => {
    const { getClient } = await import("@/lib/api/clients");
    vi.mocked(getClient).mockReturnValue(new Promise(() => {})); // never resolves
    await renderPage();
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("shows an error state when the client fetch fails", async () => {
    const { getClient } = await import("@/lib/api/clients");
    vi.mocked(getClient).mockRejectedValue(new Error("boom"));
    await renderPage();
    await waitFor(() => expect(screen.getByText(/failed to load client/i)).toBeInTheDocument());
  });

  it("renders the client's name and member id once loaded", async () => {
    const { getClient } = await import("@/lib/api/clients");
    vi.mocked(getClient).mockResolvedValue({ data: mockClient });
    await renderPage();
    await waitFor(() => expect(screen.getByText("Jane Doe")).toBeInTheDocument());
    expect(screen.getByText(/MBR-1/)).toBeInTheDocument();
  });
});
