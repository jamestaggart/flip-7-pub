import { defineConfig } from '@playwright/test';

const browserPath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  workers: 1,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    headless: true,
    launchOptions: browserPath
      ? {
          executablePath: browserPath,
        }
      : undefined,
  },
});
