import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ClientFormDialog } from "@/components/clients/client-form-dialog";

vi.mock("@/lib/api/clients", () => ({
  createClient: vi.fn(),
  updateClient: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe("ClientFormDialog", () => {
  it("shows validation errors instead of submitting when required fields are empty", async () => {
    const user = userEvent.setup();
    const onSaved = vi.fn();
    const { createClient } = await import("@/lib/api/clients");

    render(<ClientFormDialog employees={[]} teams={[]} onSaved={onSaved} />);

    await user.click(screen.getByRole("button", { name: /add client/i }));
    await user.click(await screen.findByRole("button", { name: /create client/i }));

    await waitFor(() => {
      expect(screen.getAllByText("Required").length).toBeGreaterThan(0);
    });
    expect(createClient).not.toHaveBeenCalled();
    expect(onSaved).not.toHaveBeenCalled();
  });

  it("submits and calls onSaved when required fields are filled in", async () => {
    const user = userEvent.setup();
    const onSaved = vi.fn();
    const { createClient } = await import("@/lib/api/clients");
    vi.mocked(createClient).mockResolvedValue({
      data: { id: "1", first_name: "Jane", last_name: "Doe" },
    } as never);

    render(<ClientFormDialog employees={[]} teams={[]} onSaved={onSaved} />);

    await user.click(screen.getByRole("button", { name: /add client/i }));
    await user.type(screen.getByLabelText(/first name/i), "Jane");
    await user.type(screen.getByLabelText(/last name/i), "Doe");
    await user.type(screen.getByLabelText(/date of birth/i), "1990-01-01");
    await user.type(screen.getByLabelText(/member id/i), "MBR-1");
    await user.click(screen.getByRole("button", { name: /create client/i }));

    await waitFor(() => expect(createClient).toHaveBeenCalledTimes(1));
    expect(onSaved).toHaveBeenCalledOnce();
  });
});
