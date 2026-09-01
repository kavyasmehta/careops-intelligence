import { expect, test } from "@playwright/test";

/**
 * The one required end-to-end workflow: enter as an ops user, open the
 * work queue, drill into a critical case's client profile, go back and
 * resolve that alert, then confirm the dashboard's open-alert count
 * actually decreased — not just that a click "worked" in isolation.
 */
test("ops user resolves a critical alert from the work queue and the dashboard reflects it", async ({ page }) => {
  // 1. Enter as an ops user
  await page.goto("/");
  await page.getByRole("button", { name: /Dana Whitfield/ }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  // 2. Open the work queue
  await page.goto("/queue");
  await expect(page.getByRole("heading", { name: "Operations Work Queue" })).toBeVisible();

  // Filter down to Critical severity so we reliably land on a "critical case"
  await page.getByRole("combobox").filter({ hasText: "All severities" }).click();
  await page.getByRole("option", { name: "critical", exact: true }).click();
  await page.getByRole("combobox").filter({ hasText: "All statuses" }).click();
  await page.getByRole("option", { name: "open", exact: true }).click();

  const firstRow = page.locator("table tbody tr").first();
  await expect(firstRow).toBeVisible();
  const clientName = (await firstRow.locator("td").first().innerText()).trim();

  // 3 & 4. Select the critical case and review the client profile
  await firstRow.getByRole("link").click();
  await expect(page.getByRole("heading", { name: clientName })).toBeVisible();
  await page.getByRole("tab", { name: /Alerts & Tasks/ }).click();
  await expect(page.getByText("Critical").first()).toBeVisible();

  // Baseline for step 6: capture the dashboard's open-high-priority-alerts KPI now
  await page.goto("/dashboard");
  // KpiCard renders <Card><CardHeader><CardTitle>{label}</CardTitle></CardHeader>
  // <CardContent><p class="text-2xl">{value}</p></CardContent></Card> — two
  // levels up from the label text reaches the Card, sibling to the value.
  const kpiCard = page.locator("text=Open high-priority alerts").locator("../..");
  const before = Number((await kpiCard.locator("p.text-2xl").innerText()).trim());

  // 5. Go back and resolve that same alert. Filtering by severity only
  // (not status=open) here deliberately, so the row stays visible with an
  // updated status badge after resolving instead of dropping out of view.
  await page.goto("/alerts");
  await page.getByRole("combobox").filter({ hasText: "All severities" }).click();
  await page.getByRole("option", { name: "critical", exact: true }).click();

  const alertRow = page.locator("table tbody tr").filter({ hasText: clientName }).first();
  await expect(alertRow).toBeVisible();
  await alertRow.getByRole("button", { name: "Resolve" }).click();
  await page.getByLabel(/resolution notes/i).fill("Resolved during automated verification.");
  await page.getByRole("button", { name: "Mark resolved" }).click();
  await expect(alertRow.getByText("Resolved")).toBeVisible();

  // 6. Confirm the dashboard updates
  await page.goto("/dashboard");
  await expect
    .poll(async () => Number((await kpiCard.locator("p.text-2xl").innerText()).trim()))
    .toBe(before - 1);
});
