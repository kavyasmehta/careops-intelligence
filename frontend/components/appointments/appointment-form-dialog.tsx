"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";

import { ClientPicker } from "@/components/client-picker";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ApiError } from "@/lib/api";
import { createAppointment } from "@/lib/api/appointments";
import { SERVICE_TYPES } from "@/lib/constants";
import { appointmentFormSchema, type AppointmentFormValues } from "@/lib/validation/appointment";
import type { Client } from "@/types/entities";

export function AppointmentFormDialog({ clients, onSaved }: { clients: Client[]; onSaved: () => void }) {
  const [open, setOpen] = useState(false);
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AppointmentFormValues>({
    resolver: zodResolver(appointmentFormSchema),
    defaultValues: {
      client_id: "",
      appointment_datetime: "",
      service_type: "",
      provider: "",
      location: "",
      status: "scheduled",
    },
  });

  const onSubmit = async (values: AppointmentFormValues) => {
    try {
      await createAppointment({ ...values, appointment_datetime: new Date(values.appointment_datetime).toISOString() });
      toast.success("Appointment scheduled");
      setOpen(false);
      reset();
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to schedule appointment");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm" />}>
        <Plus className="size-4" /> Schedule Appointment
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Schedule Appointment</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label>Client</Label>
            <Controller
              control={control}
              name="client_id"
              render={({ field }) => <ClientPicker clients={clients} value={field.value} onChange={field.onChange} />}
            />
            {errors.client_id && <p className="text-xs text-destructive">{errors.client_id.message}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="appointment_datetime">Date &amp; time</Label>
            <Input id="appointment_datetime" type="datetime-local" {...register("appointment_datetime")} />
            {errors.appointment_datetime && (
              <p className="text-xs text-destructive">{errors.appointment_datetime.message}</p>
            )}
          </div>
          <div className="space-y-1.5">
            <Label>Service type</Label>
            <Controller
              control={control}
              name="service_type"
              render={({ field }) => (
                <Select value={field.value || undefined} onValueChange={field.onChange}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select service" />
                  </SelectTrigger>
                  <SelectContent>
                    {SERVICE_TYPES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {errors.service_type && <p className="text-xs text-destructive">{errors.service_type.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="provider">Provider</Label>
              <Input id="provider" {...register("provider")} />
              {errors.provider && <p className="text-xs text-destructive">{errors.provider.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="location">Location</Label>
              <Input id="location" {...register("location")} />
              {errors.location && <p className="text-xs text-destructive">{errors.location.message}</p>}
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting}>
              Schedule
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
