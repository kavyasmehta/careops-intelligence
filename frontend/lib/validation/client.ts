import { z } from "zod";

export const clientFormSchema = z.object({
  first_name: z.string().min(1, "Required"),
  last_name: z.string().min(1, "Required"),
  date_of_birth: z.string().min(1, "Required"),
  member_id: z.string().min(1, "Required"),
  email: z.union([z.string().email("Invalid email"), z.literal("")]).optional(),
  phone: z.string().optional(),
  address_line1: z.string().optional(),
  address_city: z.string().optional(),
  address_state: z.string().optional(),
  address_zip: z.string().optional(),
  assigned_team_id: z.string().optional(),
  assigned_employee_id: z.string().optional(),
  status: z.enum(["active", "pending", "inactive", "discharged"]),
});

export type ClientFormValues = z.infer<typeof clientFormSchema>;
