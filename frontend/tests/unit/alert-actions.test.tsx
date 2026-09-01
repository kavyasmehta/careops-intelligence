import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ResolveAlertDialog } from "@/components/alerts/resolve-alert-dialog";

vi.mock("@/lib/api/alerts", () => ({
  updateAlert: vi.fn().mockResolvedValue({ data: {} }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe("ResolveAlertDialog", () => {
  it("calls updateAlert with status=resolved and the entered notes", async () => {
    const user = userEvent.setup();
    const onSaved = vi.fn();
    const { updateAlert } = await import("@/lib/api/alerts");

    render(<ResolveAlertDialog alertId="alert-1" onSaved={onSaved} />);

    await user.click(screen.getByRole("button", { name: /resolve/i }));
    await user.type(await screen.findByLabelText(/resolution notes/i), "Confirmed with payer");
    await user.click(screen.getByRole("button", { name: /mark resolved/i }));

    await waitFor(() =>
      expect(updateAlert).toHaveBeenCalledWith("alert-1", {
        status: "resolved",
        resolution_notes: "Confirmed with payer",
      }),
    );
    expect(onSaved).toHaveBeenCalledOnce();
  });
});
