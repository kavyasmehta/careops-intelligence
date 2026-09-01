"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useDemoSession } from "@/contexts/demo-session-context";
import { BRAND_ICON, BRAND_NAME, NAV_ITEMS } from "@/lib/nav-config";
import { ROLE_LABELS } from "@/lib/demo-session";

export function AppSidebar() {
  const pathname = usePathname();
  const { session } = useDemoSession();
  const BrandIcon = BRAND_ICON;

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-1.5">
          <BrandIcon className="size-5 shrink-0 text-sidebar-primary" />
          <span className="truncate text-sm font-semibold group-data-[collapsible=icon]:hidden">
            {BRAND_NAME}
          </span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_ITEMS.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton render={<Link href={item.href} />} isActive={isActive} tooltip={item.label}>
                      <item.icon />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        {session && (
          <div className="px-2 py-1.5 text-xs text-sidebar-foreground/70 group-data-[collapsible=icon]:hidden">
            <p className="truncate font-medium text-sidebar-foreground">{session.name}</p>
            <p className="truncate">{ROLE_LABELS[session.role]}</p>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
