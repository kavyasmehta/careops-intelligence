import { z } from "zod";

export const appointmentFormSchema = z.object({
  client_id: z.string().min(1, "Select a client"),
  appointment_datetime: z.string().min(1, "Required"),
  service_type: z.string().min(1, "Required"),
  provider: z.string().min(1, "Required"),
  location: z.string().min(1, "Required"),
  status: z.enum(["scheduled", "completed", "cancelled", "no_show"]),
});

export type AppointmentFormValues = z.infer<typeof appointmentFormSchema>;
