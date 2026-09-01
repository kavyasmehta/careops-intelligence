import { getStoredSession } from "@/lib/demo-session";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface ListResponse<T> {
  data: T[];
  meta: PageMeta;
}

export interface ItemResponse<T> {
  data: T;
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Thin fetch wrapper: attaches the demo role/user headers, normalizes
 * errors into ApiError with the backend's actual message, and types
 * the JSON response. Every entity-specific API function (lib/api/*)
 * builds on this rather than calling fetch directly.
 */
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const session = getStoredSession();
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (session) {
    headers.set("X-Demo-Role", session.role);
    headers.set("X-Demo-User", session.name);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    let message = response.statusText || `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body?.error?.message ?? message;
    } catch {
      // response wasn't JSON — keep the status-text fallback
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

function buildQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export { API_BASE_URL, buildQuery };
