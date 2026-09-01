/**
 * Demo "who am I" session — there is no real authentication in this
 * portfolio app. The user picks a seeded employee on the entry page;
 * that choice is persisted here and read both by the UI (topbar,
 * sidebar) and by the API client (to set X-Demo-Role / X-Demo-User on
 * every request). Single source of truth so the two never disagree.
 */
export type DemoRole = "operations_manager" | "intake_specialist" | "authorization_specialist";

export interface DemoSession {
  userId: string;
  name: string;
  role: DemoRole;
  teamId: string | null;
}

export const ROLE_LABELS: Record<DemoRole, string> = {
  operations_manager: "Operations Manager",
  intake_specialist: "Intake Specialist",
  authorization_specialist: "Authorization Specialist",
};

const STORAGE_KEY = "careops-demo-session";

export function getStoredSession(): DemoSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as DemoSession) : null;
  } catch {
    return null;
  }
}

export function saveSession(session: DemoSession): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch {
    // localStorage unavailable (private mode, etc.) — session just won't persist across reloads.
  }
}

export function clearStoredSession(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // no-op
  }
}
