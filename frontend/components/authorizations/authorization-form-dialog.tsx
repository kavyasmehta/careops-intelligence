"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState, type ReactElement, type ReactNode } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";

import { ClientPicker } from "@/components/client-picker";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ApiError } from "@/lib/api";
import { createAuthorization } from "@/lib/api/authorizations";
import { PAYERS, SERVICE_TYPES } from "@/lib/constants";
import { authorizationFormSchema, type AuthorizationFormValues } from "@/lib/validation/authorization";
import type { Client } from "@/types/entities";

const STATUS_OPTIONS = ["pending", "active", "expired", "exhausted", "denied"] as const;

export function AuthorizationFormDialog({
  clients,
  triggerContent,
  triggerElement,
  onSaved,
}: {
  clients: Client[];
  triggerContent?: ReactNode;
  triggerElement?: ReactElement;
  onSaved: () => void;
}) {
  const [open, setOpen] = useState(false);
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AuthorizationFormValues>({
    resolver: zodResolver(authorizationFormSchema),
    defaultValues: {
      client_id: "",
      payer: "",
      authorization_number: "",
      service_type: "",
      units_approved: 10,
      units_used: 0,
      effective_date: "",
      expiration_date: "",
      status: "pending",
    },
  });

  const onSubmit = async (values: AuthorizationFormValues) => {
    try {
      await createAuthorization(values);
      toast.success("Authorization created");
      setOpen(false);
      reset();
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to create authorization");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={triggerElement ?? <Button size="sm" />}>
        {triggerContent ?? (
          <>
            <Plus className="size-4" /> New Authorization
          </>
        )}
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Authorization</DialogTitle>
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
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Payer</Label>
              <Controller
                control={control}
                name="payer"
                render={({ field }) => (
                  <Select value={field.value || undefined} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select payer" />
                    </SelectTrigger>
                    <SelectContent>
                      {PAYERS.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.payer && <p className="text-xs text-destructive">{errors.payer.message}</p>}
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
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="authorization_number">Authorization number</Label>
            <Input id="authorization_number" {...register("authorization_number")} />
            {errors.authorization_number && (
              <p className="text-xs text-destructive">{errors.authorization_number.message}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="units_approved">Units approved</Label>
              <Input id="units_approved" type="number" {...register("units_approved", { valueAsNumber: true })} />
              {errors.units_approved && <p className="text-xs text-destructive">{errors.units_approved.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="units_used">Units used</Label>
              <Input id="units_used" type="number" {...register("units_used", { valueAsNumber: true })} />
              {errors.units_used && <p className="text-xs text-destructive">{errors.units_used.message}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="effective_date">Effective date</Label>
              <Input id="effective_date" type="date" {...register("effective_date")} />
              {errors.effective_date && <p className="text-xs text-destructive">{errors.effective_date.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="expiration_date">Expiration date</Label>
              <Input id="expiration_date" type="date" {...register("expiration_date")} />
              {errors.expiration_date && <p className="text-xs text-destructive">{errors.expiration_date.message}</p>}
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Status</Label>
            <Controller
              control={control}
              name="status"
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting}>
              Create authorization
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
