import { defineConfig, devices } from "@playwright/test";

/**
 * Runs against the full docker-compose stack (frontend + backend + Mongo +
 * Neo4j), not a single dev server Playwright could start itself — bring the
 * stack up first with `docker compose up` (see README) before running this.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
