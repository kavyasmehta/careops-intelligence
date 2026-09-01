import {
  Activity,
  BarChart3,
  Bell,
  CalendarClock,
  ClipboardList,
  FileCheck2,
  LayoutDashboard,
  Network,
  ShieldCheck,
  Users,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/queue", label: "Work Queue", icon: ClipboardList },
  { href: "/clients", label: "Clients", icon: Users },
  { href: "/eligibility", label: "Eligibility", icon: ShieldCheck },
  { href: "/authorizations", label: "Authorizations", icon: FileCheck2 },
  { href: "/appointments", label: "Appointments", icon: CalendarClock },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/network", label: "Network Intelligence", icon: Network },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export const BRAND_ICON = Activity;
export const BRAND_NAME = "CareOps Intelligence";
