"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { AppSidebar } from "@/components/app-sidebar";
import { AppTopbar } from "@/components/app-topbar";
import { DisclaimerBanner } from "@/components/disclaimer-banner";
import { LoadingState } from "@/components/states/loading-state";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { useDemoSession } from "@/contexts/demo-session-context";

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  const { session, isLoaded } = useDemoSession();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !session) {
      router.replace("/");
    }
  }, [isLoaded, session, router]);

  if (!isLoaded || !session) {
    return (
      <div className="flex min-h-svh items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <LoadingState rows={3} />
        </div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <DisclaimerBanner />
        <AppTopbar />
        <main className="flex flex-1 flex-col gap-4 p-4 md:p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
