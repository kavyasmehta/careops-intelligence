"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, type ListResponse } from "@/lib/api";

type PagedParams = { page: number; page_size: number; sort?: string };

export function usePaginatedList<T, TFilters extends object>(
  fetchFn: (params: TFilters & PagedParams) => Promise<ListResponse<T>>,
  initialFilters: TFilters,
  pageSize = 10,
) {
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<string | undefined>(undefined);
  const [filters, setFiltersState] = useState<TFilters>(initialFilters);
  const [data, setData] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    setIsLoading(true);
    setError(null);
    fetchFn({ ...filters, page, page_size: pageSize, sort } as TFilters & PagedParams)
      .then((res) => {
        setData(res.data);
        setTotal(res.meta.total);
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Failed to load data.");
      })
      .finally(() => setIsLoading(false));
    // fetchFn is expected to be stable (module-level API function); filters/page/sort drive refetches.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, page, pageSize, sort]);

  useEffect(() => {
    // Fetch-on-dependency-change: the canonical data-fetching effect
    // pattern (https://react.dev/learn/synchronizing-with-effects#fetching-data).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refetch();
  }, [refetch]);

  const updateFilters = (next: Partial<TFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...next }));
    setPage(1);
  };

  return {
    data,
    total,
    page,
    setPage,
    pageSize,
    sort,
    setSort,
    filters,
    updateFilters,
    isLoading,
    error,
    refetch,
  };
}
