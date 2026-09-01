import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { usePaginatedList } from "@/hooks/use-paginated-list";

function makeFetchFn() {
  return vi.fn().mockResolvedValue({ data: [{ id: "1" }], meta: { page: 1, page_size: 10, total: 1 } });
}

describe("usePaginatedList", () => {
  it("fetches on mount with the initial filters and page 1", async () => {
    const fetchFn = makeFetchFn();
    renderHook(() => usePaginatedList(fetchFn, { status: "active" }, 10));

    await waitFor(() => expect(fetchFn).toHaveBeenCalledTimes(1));
    expect(fetchFn).toHaveBeenCalledWith(expect.objectContaining({ status: "active", page: 1, page_size: 10 }));
  });

  it("resets to page 1 and refetches when filters change", async () => {
    const fetchFn = makeFetchFn();
    const { result } = renderHook(() => usePaginatedList(fetchFn, { status: "" }, 10));
    await waitFor(() => expect(fetchFn).toHaveBeenCalledTimes(1));

    act(() => result.current.setPage(3));
    await waitFor(() => expect(fetchFn).toHaveBeenCalledTimes(2));
    expect(fetchFn).toHaveBeenLastCalledWith(expect.objectContaining({ page: 3 }));

    act(() => result.current.updateFilters({ status: "resolved" }));
    await waitFor(() => expect(fetchFn).toHaveBeenCalledTimes(3));
    expect(fetchFn).toHaveBeenLastCalledWith(expect.objectContaining({ status: "resolved", page: 1 }));
  });

  it("surfaces a fetch failure as an error instead of throwing", async () => {
    const fetchFn = vi.fn().mockRejectedValue(new Error("network down"));
    const { result } = renderHook(() => usePaginatedList(fetchFn, {}, 10));

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBeTruthy();
    expect(result.current.data).toEqual([]);
  });
});
