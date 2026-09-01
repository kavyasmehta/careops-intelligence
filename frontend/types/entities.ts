import type { DemoRole } from "@/lib/demo-session";

export interface User {
  id: string;
  name: string;
  role: DemoRole;
  team_id: string | null;
  created_at: string;
  updated_at: string;
}
