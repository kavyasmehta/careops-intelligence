"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Client } from "@/types/entities";

export function ClientPicker({
  clients,
  value,
  onChange,
  placeholder = "Select client",
}: {
  clients: Client[];
  value: string;
  onChange: (id: string) => void;
  placeholder?: string;
}) {
  const sorted = [...clients].sort((a, b) =>
    `${a.last_name}${a.first_name}`.localeCompare(`${b.last_name}${b.first_name}`),
  );
  const byId = new Map(clients.map((c) => [c.id, c]));
  // Base UI's SelectValue shows the raw value string by default — it doesn't
  // track the matched SelectItem's rendered label the way Radix does. Since
  // the stored value here is an opaque client id, we resolve the label
  // ourselves via the children render-function form.
  const label = (id: string | null) => {
    const c = id ? byId.get(id) : undefined;
    return c ? `${c.last_name}, ${c.first_name} (${c.member_id})` : placeholder;
  };

  return (
    // key={value}: Base UI's SelectValue render-function only re-evaluates
    // reliably in response to the Select's own internal interactions, not
    // to the `value` prop changing programmatically from outside (e.g. a
    // "similar client" shortcut elsewhere on the page calling onChange
    // directly). Remounting on value keeps the displayed label correct
    // either way.
    <Select key={value} value={value || undefined} onValueChange={(next) => onChange(next ?? "")}>
      <SelectTrigger className="w-full">
        <SelectValue placeholder={placeholder}>{label}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        {sorted.map((c) => (
          <SelectItem key={c.id} value={c.id}>
            {c.last_name}, {c.first_name} ({c.member_id})
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
