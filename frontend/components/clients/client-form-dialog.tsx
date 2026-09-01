"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useEffect, useState, type ReactElement, type ReactNode } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ApiError } from "@/lib/api";
import { createClient, updateClient, type ClientInput } from "@/lib/api/clients";
import { clientFormSchema, type ClientFormValues } from "@/lib/validation/client";
import type { Client, User } from "@/types/entities";

const STATUS_OPTIONS = ["active", "pending", "inactive", "discharged"] as const;

function toFormValues(client?: Client): ClientFormValues {
  return {
    first_name: client?.first_name ?? "",
    last_name: client?.last_name ?? "",
    date_of_birth: client?.date_of_birth ?? "",
    member_id: client?.member_id ?? "",
    email: client?.email ?? "",
    phone: client?.phone ?? "",
    address_line1: client?.address?.line1 ?? "",
    address_city: client?.address?.city ?? "",
    address_state: client?.address?.state ?? "",
    address_zip: client?.address?.zip ?? "",
    assigned_team_id: client?.assigned_team_id ?? "",
    assigned_employee_id: client?.assigned_employee_id ?? "",
    status: client?.status ?? "pending",
  };
}

export function ClientFormDialog({
  client,
  employees,
  teams,
  triggerContent,
  triggerElement,
  onSaved,
}: {
  client?: Client;
  employees: User[];
  teams: string[];
  /** Visible content of the trigger (icon/text) — kept separate from the
   * styled wrapper element so Base UI's `render` composition (which the
   * wrapper occupies) never has to guess how to merge two sets of children. */
  triggerContent?: ReactNode;
  triggerElement?: ReactElement;
  onSaved: () => void;
}) {
  const [open, setOpen] = useState(false);
  const isEdit = Boolean(client);
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ClientFormValues>({
    resolver: zodResolver(clientFormSchema),
    defaultValues: toFormValues(client),
  });

  useEffect(() => {
    if (open) reset(toFormValues(client));
  }, [open, client, reset]);

  const onSubmit = async (values: ClientFormValues) => {
    const payload: ClientInput = {
      first_name: values.first_name,
      last_name: values.last_name,
      date_of_birth: values.date_of_birth,
      member_id: values.member_id,
      email: values.email || null,
      phone: values.phone || null,
      address: values.address_line1
        ? {
            line1: values.address_line1,
            city: values.address_city ?? "",
            state: values.address_state ?? "",
            zip: values.address_zip ?? "",
          }
        : null,
      assigned_team_id: values.assigned_team_id || null,
      assigned_employee_id: values.assigned_employee_id || null,
      status: values.status,
    };
    try {
      if (isEdit && client) {
        await updateClient(client.id, payload);
        toast.success("Client updated");
      } else {
        await createClient(payload);
        toast.success("Client created");
      }
      setOpen(false);
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={triggerElement ?? <Button size="sm" />}>
        {triggerContent ?? (
          <>
            <Plus className="size-4" /> Add Client
          </>
        )}
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Client" : "Add Client"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="first_name">First name</Label>
              <Input id="first_name" {...register("first_name")} />
              {errors.first_name && <p className="text-xs text-destructive">{errors.first_name.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="last_name">Last name</Label>
              <Input id="last_name" {...register("last_name")} />
              {errors.last_name && <p className="text-xs text-destructive">{errors.last_name.message}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="date_of_birth">Date of birth</Label>
              <Input id="date_of_birth" type="date" {...register("date_of_birth")} />
              {errors.date_of_birth && <p className="text-xs text-destructive">{errors.date_of_birth.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="member_id">Member ID</Label>
              <Input id="member_id" {...register("member_id")} />
              {errors.member_id && <p className="text-xs text-destructive">{errors.member_id.message}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" {...register("phone")} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="address_line1">Address</Label>
            <Input id="address_line1" placeholder="Street address" {...register("address_line1")} />
            <div className="grid grid-cols-3 gap-2">
              <Input placeholder="City" {...register("address_city")} />
              <Input placeholder="State" {...register("address_state")} />
              <Input placeholder="ZIP" {...register("address_zip")} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Assigned team</Label>
              <Controller
                control={control}
                name="assigned_team_id"
                render={({ field }) => (
                  <Select value={field.value || undefined} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Unassigned" />
                    </SelectTrigger>
                    <SelectContent>
                      {teams.map((team) => (
                        <SelectItem key={team} value={team}>
                          {team}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Assigned employee</Label>
              <Controller
                control={control}
                name="assigned_employee_id"
                render={({ field }) => {
                  // Stored value is an opaque employee id — see ClientPicker
                  // for why SelectValue needs the render-function form here.
                  const byId = new Map(employees.map((e) => [e.id, e]));
                  return (
                    <Select value={field.value || undefined} onValueChange={field.onChange}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Unassigned">
                          {(id: string | null) => (id ? byId.get(id)?.name ?? "Unassigned" : "Unassigned")}
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {employees.map((emp) => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  );
                }}
              />
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
                    {STATUS_OPTIONS.map((status) => (
                      <SelectItem key={status} value={status}>
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting}>
              {isEdit ? "Save changes" : "Create client"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
