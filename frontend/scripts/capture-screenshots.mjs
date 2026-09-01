// One-off script (not part of the test suite) to capture real screenshots
// of the running app for the README. Run with the full docker-compose
// stack up and seeded: `node scripts/capture-screenshots.mjs`.
import { chromium } from "@playwright/test";
import { mkdirSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.resolve(__dirname, "../../docs/screenshots");
mkdirSync(OUT_DIR, { recursive: true });

const BASE_URL = "http://localhost:3000";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  await page.goto(BASE_URL);
  await page.screenshot({ path: path.join(OUT_DIR, "01-entry.png") });

  await page.getByRole("button", { name: /Dana Whitfield/ }).click();
  await page.waitForURL(/\/dashboard/);
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(OUT_DIR, "02-dashboard.png") });

  await page.goto(`${BASE_URL}/queue`);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(OUT_DIR, "03-work-queue.png") });

  await page.goto(`${BASE_URL}/clients`);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(OUT_DIR, "04-client-directory.png") });

  const firstClientLink = page.locator("table tbody tr a").first();
  await firstClientLink.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(OUT_DIR, "05-client-360.png") });

  await page.goto(`${BASE_URL}/alerts`);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(OUT_DIR, "06-alert-center.png") });

  await page.goto(`${BASE_URL}/network`);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(OUT_DIR, "07-network-intelligence.png") });

  await page.getByRole("combobox").filter({ hasText: "Select client" }).click();
  await page.getByRole("option").first().click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(OUT_DIR, "07b-client-ego-network.png") });

  await page.goto(`${BASE_URL}/analytics`);
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(OUT_DIR, "08-analytics.png") });

  await browser.close();
  console.log("Screenshots saved to", OUT_DIR);
}

main();
