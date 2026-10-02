import { defineConfig } from '@playwright/test';
import os from 'node:os';
import path from 'node:path';

const frontendDirectory = __dirname;
const backendDirectory = path.resolve(frontendDirectory, '../backend');
const python = path.join(backendDirectory, '.venv', 'bin', 'python');
const databasePath = path.join(os.tmpdir(), `turfmate-playwright-${process.pid}.db`);
const apiUrl = 'http://127.0.0.1:4810/api';
const frontendUrl = 'http://127.0.0.1:4310';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: frontendUrl,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: `${python} -m scripts.seed && ${python} -m uvicorn app.main:app --host 127.0.0.1 --port 4810`,
      cwd: backendDirectory,
      url: 'http://127.0.0.1:4810/health',
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        DATABASE_URL: `sqlite:///${databasePath}`,
        FRONTEND_URL: frontendUrl,
      },
    },
    {
      command: 'npm run dev -- --hostname 127.0.0.1 --port 4310',
      cwd: frontendDirectory,
      url: frontendUrl,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        NEXT_PUBLIC_API_URL: apiUrl,
        NEXT_DIST_DIR: '.next-e2e',
      },
    },
  ],
});