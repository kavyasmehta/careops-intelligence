import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";

describe("LoadingState", () => {
  it("renders the requested number of skeleton rows", () => {
    render(<LoadingState rows={3} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});

describe("ErrorState", () => {
  it("shows the provided message", () => {
    render(<ErrorState message="Could not reach the API." />);
    expect(screen.getByText("Could not reach the API.")).toBeInTheDocument();
  });

  it("calls onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    const { default: userEvent } = await import("@testing-library/user-event");
    render(<ErrorState message="Failed" onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("omits the retry button when onRetry isn't provided", () => {
    render(<ErrorState message="Failed" />);
    expect(screen.queryByRole("button", { name: /try again/i })).not.toBeInTheDocument();
  });
});

describe("EmptyState", () => {
  it("renders the default title and a custom description", () => {
    render(<EmptyState description="No records match these filters." />);
    expect(screen.getByText("Nothing here yet")).toBeInTheDocument();
    expect(screen.getByText("No records match these filters.")).toBeInTheDocument();
  });
});
