"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { DisclaimerBanner } from "@/components/disclaimer-banner";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDemoSession } from "@/contexts/demo-session-context";
import { ApiError } from "@/lib/api";
import { listUsers } from "@/lib/api/users";
import { ROLE_LABELS, type DemoRole } from "@/lib/demo-session";
import { BRAND_ICON, BRAND_NAME } from "@/lib/nav-config";
import type { User } from "@/types/entities";

const ROLE_ORDER: DemoRole[] = ["operations_manager", "intake_specialist", "authorization_specialist"];

export default function EntryPage() {
  const router = useRouter();
  const { setSession } = useDemoSession();
  const [users, setUsers] = useState<User[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadUsers = () => {
    setError(null);
    setUsers(null);
    listUsers()
      .then((res) => setUsers(res.data))
      .catch((err: unknown) => {
        const message =
          err instanceof ApiError
            ? `${err.message} (is the backend running and seeded?)`
            : "Could not reach the CareOps API. Is the backend running?";
        setError(message);
      });
  };

  // Fetch-on-mount: resets state and kicks off the request. Not the
  // cascading-render pattern the lint rule targets — no derived state loop.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(loadUsers, []);

  const enterAs = (user: User) => {
    setSession({ userId: user.id, name: user.name, role: user.role, teamId: user.team_id });
    router.push("/dashboard");
  };

  const BrandIcon = BRAND_ICON;

  return (
    <div className="flex min-h-svh flex-col">
      <DisclaimerBanner />
      <div className="flex flex-1 flex-col items-center justify-center gap-8 bg-muted/30 px-4 py-12">
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="flex items-center gap-2">
            <BrandIcon className="size-8 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">{BRAND_NAME}</h1>
          </div>
          <p className="max-w-md text-sm text-muted-foreground">
            Healthcare operations management and analytics — centralizing eligibility, authorizations,
            appointments, and operational alerts for care teams.
          </p>
        </div>

        <div className="w-full max-w-4xl">
          <Card>
            <CardHeader>
              <CardTitle>Enter the demo as...</CardTitle>
            </CardHeader>
            <CardContent>
              {error && <ErrorState message={error} onRetry={loadUsers} />}
              {!error && !users && <LoadingState rows={5} />}
              {!error && users && (
                <div className="grid gap-6 sm:grid-cols-3">
                  {ROLE_ORDER.map((role) => (
                    <div key={role} className="space-y-2">
                      <h3 className="text-sm font-semibold text-muted-foreground">{ROLE_LABELS[role]}</h3>
                      <div className="space-y-2">
                        {users
                          .filter((u) => u.role === role)
                          .map((user) => (
                            <button
                              key={user.id}
                              onClick={() => enterAs(user)}
                              className="w-full rounded-md border bg-card px-3 py-2 text-left text-sm shadow-sm transition-colors hover:border-primary hover:bg-accent"
                            >
                              <div className="font-medium">{user.name}</div>
                              {user.team_id && <div className="text-xs text-muted-foreground">{user.team_id}</div>}
                            </button>
                          ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
