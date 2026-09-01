import { z } from "zod";

export const authorizationFormSchema = z
  .object({
    client_id: z.string().min(1, "Select a client"),
    payer: z.string().min(1, "Required"),
    authorization_number: z.string().min(1, "Required"),
    service_type: z.string().min(1, "Required"),
    units_approved: z.number({ message: "Required" }).int().positive("Must be greater than 0"),
    units_used: z.number({ message: "Required" }).int().min(0),
    effective_date: z.string().min(1, "Required"),
    expiration_date: z.string().min(1, "Required"),
    status: z.enum(["pending", "active", "expired", "exhausted", "denied"]),
  })
  .refine((v) => v.expiration_date > v.effective_date, {
    message: "Expiration must be after effective date",
    path: ["expiration_date"],
  })
  .refine((v) => v.units_used <= v.units_approved, {
    message: "Units used cannot exceed units approved",
    path: ["units_used"],
  });

export type AuthorizationFormValues = z.infer<typeof authorizationFormSchema>;
