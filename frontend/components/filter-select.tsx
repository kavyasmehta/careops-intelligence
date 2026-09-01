"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface FilterSelectOption {
  value: string;
  label: string;
}

/**
 * The "All X" filter dropdown pattern repeated across every list page.
 * Centralizing it also fixes a real bug it was previously affected by
 * individually: Base UI's SelectValue shows the raw value string by
 * default (unlike Radix, it doesn't track the matched item's label) —
 * so the "all" sentinel value rendered as the literal text "all"
 * instead of e.g. "All severities". See ClientPicker for the same
 * root cause. Fixed once here via the children render-function form.
 */
export function FilterSelect({
  value,
  onChange,
  options,
  allLabel,
  placeholder,
  className = "w-40",
}: {
  value: string;
  onChange: (value: string) => void;
  options: FilterSelectOption[];
  allLabel: string;
  placeholder?: string;
  className?: string;
}) {
  const labelFor = (v: string | null) => {
    if (!v || v === "all") return allLabel;
    return options.find((o) => o.value === v)?.label ?? v;
  };

  return (
    <Select value={value || "all"} onValueChange={(next) => onChange(!next || next === "all" ? "" : next)}>
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder}>{labelFor}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">{allLabel}</SelectItem>
        {options.map((o) => (
          <SelectItem key={o.value} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
