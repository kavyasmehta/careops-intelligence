"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import {
  clearStoredSession,
  getStoredSession,
  saveSession,
  type DemoSession,
} from "@/lib/demo-session";

interface DemoSessionContextValue {
  session: DemoSession | null;
  isLoaded: boolean;
  setSession: (session: DemoSession) => void;
  signOut: () => void;
}

const DemoSessionContext = createContext<DemoSessionContextValue | undefined>(undefined);

export function DemoSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<DemoSession | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Reading localStorage must happen post-mount (client-only) to avoid an
    // SSR/hydration mismatch — this is the standard pattern, not the
    // cascading-render case the lint rule is meant to catch.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSessionState(getStoredSession());
    setIsLoaded(true);
  }, []);

  const setSession = (next: DemoSession) => {
    setSessionState(next);
    saveSession(next);
  };

  const signOut = () => {
    setSessionState(null);
    clearStoredSession();
  };

  return (
    <DemoSessionContext.Provider value={{ session, isLoaded, setSession, signOut }}>
      {children}
    </DemoSessionContext.Provider>
  );
}

export function useDemoSession(): DemoSessionContextValue {
  const ctx = useContext(DemoSessionContext);
  if (!ctx) {
    throw new Error("useDemoSession must be used within a DemoSessionProvider");
  }
  return ctx;
}
