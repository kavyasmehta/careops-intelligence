"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { useDemoSession } from "@/contexts/demo-session-context";
import { ROLE_LABELS } from "@/lib/demo-session";

export function AppTopbar() {
  const router = useRouter();
  const { session, signOut } = useDemoSession();

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-5" />
      <div className="flex-1 text-sm text-muted-foreground">
        {session ? `Viewing as ${session.name} — ${ROLE_LABELS[session.role]}` : null}
      </div>
      <ThemeToggle />
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          signOut();
          router.push("/");
        }}
      >
        <LogOut className="size-4" />
        Switch user
      </Button>
    </header>
  );
}
