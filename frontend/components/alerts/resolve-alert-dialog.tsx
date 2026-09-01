"use client";

import { CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { updateAlert } from "@/lib/api/alerts";

export function ResolveAlertDialog({ alertId, onSaved }: { alertId: string; onSaved: () => void }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const resolve = async () => {
    setSubmitting(true);
    try {
      await updateAlert(alertId, { status: "resolved", resolution_notes: notes || null });
      toast.success("Alert resolved");
      setOpen(false);
      setNotes("");
      onSaved();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to resolve alert");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="outline" size="sm" />}>
        <CheckCircle2 className="size-4" /> Resolve
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Resolve alert</DialogTitle>
        </DialogHeader>
        <div className="space-y-1.5">
          <Label htmlFor="resolution_notes">Resolution notes (optional)</Label>
          <Textarea
            id="resolution_notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What was done to resolve this?"
          />
        </div>
        <DialogFooter>
          <Button onClick={resolve} disabled={submitting}>
            Mark resolved
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
