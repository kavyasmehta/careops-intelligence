"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { PlayCircle } from "lucide-react";
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
import { createEligibilityCheck } from "@/lib/api/eligibility";
import { PAYERS } from "@/lib/constants";
import { eligibilityFormSchema, type EligibilityFormValues } from "@/lib/validation/eligibility";
import type { Client } from "@/types/entities";

const FAILURE_REASONS = [
  "Member ID not found",
  "Coverage terminated prior to service date",
  "Plan not active for requested service",
  "Payer system error during verification",
  "Client ineligible for requested service type",
];

/**
 * "Manual check simulation" from the spec: there's no real payer
 * connection, so this simulates the outcome the operator selects and
 * writes a real EligibilityCheck record — same shape as an automated
 * check would produce.
 */
export function RunCheckDialog({ clients, onSaved }: { clients: Client[]; onSaved: () => void }) {
  const [open, setOpen] = useState(false);
  const {
    control,
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EligibilityFormValues>({
    resolver: zodResolver(eligibilityFormSchema),
    defaultValues: { client_id: "", payer: "", coverage_status: "active", plan_name: "", failure_reason: "" },
  });
  const status = watch("coverage_status");

  const onSubmit = async (values: EligibilityFormValues) => {
    try {
      await createEligibilityCheck({
        client_id: values.client_id,
        payer: values.payer,
        check_date: new Date().toISOString(),
        coverage_status: values.coverage_status,
        plan_name: values.plan_name || null,
        failure_reason: values.coverage_status === "failed" ? values.failure_reason || FAILURE_REASONS[0] : null,
        source: "manual",
      });
      toast.success("Eligibility check recorded");
      setOpen(false);
      reset();
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to run check");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm" />}>
        <PlayCircle className="size-4" /> Run Eligibility Check
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Run Eligibility Check</DialogTitle>
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
            <Label>Result</Label>
            <Controller
              control={control}
              name="coverage_status"
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active — coverage confirmed</SelectItem>
                    <SelectItem value="failed">Failed — could not verify</SelectItem>
                    <SelectItem value="pending">Pending — payer response delayed</SelectItem>
                    <SelectItem value="inactive">Inactive — coverage lapsed</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          {status === "failed" && (
            <div className="space-y-1.5">
              <Label>Failure reason</Label>
              <Controller
                control={control}
                name="failure_reason"
                render={({ field }) => (
                  <Select value={field.value || undefined} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select reason" />
                    </SelectTrigger>
                    <SelectContent>
                      {FAILURE_REASONS.map((r) => (
                        <SelectItem key={r} value={r}>
                          {r}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
          )}
          <div className="space-y-1.5">
            <Label htmlFor="plan_name">Plan name (optional)</Label>
            <Input id="plan_name" {...register("plan_name")} />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting}>
              Submit
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
