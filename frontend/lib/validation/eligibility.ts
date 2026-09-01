import { z } from "zod";

export const eligibilityFormSchema = z.object({
  client_id: z.string().min(1, "Select a client"),
  payer: z.string().min(1, "Required"),
  coverage_status: z.enum(["active", "inactive", "failed", "pending"]),
  plan_name: z.string().optional(),
  failure_reason: z.string().optional(),
});

export type EligibilityFormValues = z.infer<typeof eligibilityFormSchema>;
