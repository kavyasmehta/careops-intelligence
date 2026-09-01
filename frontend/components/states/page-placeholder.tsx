import type { LucideIcon } from "lucide-react";
import { Construction } from "lucide-react";

/**
 * Honest "not built yet" marker for routes whose nav entry exists
 * (Phase 5 app shell) but whose real content lands in a later phase —
 * deliberately not a fake implementation of the feature.
 */
export function PagePlaceholder({
  title,
  phase,
  icon: Icon = Construction,
}: {
  title: string;
  phase: string;
  icon?: LucideIcon;
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 rounded-lg border border-dashed p-16 text-center">
      <Icon className="size-10 text-muted-foreground" />
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">
        This page&apos;s navigation and layout are wired up now; the full feature lands in {phase}.
      </p>
    </div>
  );
}
