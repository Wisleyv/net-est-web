import { defineConfig, devices } from '@playwright/test';

// Playwright configuration for NET-EST frontend E2E tests
// - Spins up backend FastAPI and Vite dev server
// - Uses a stable baseURL so tests can use relative paths

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 120_000,
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    headless: true,
  },
  // Run both backend and frontend servers. Reuse if they're already running.
  webServer: [
    {
      // Start backend (FastAPI)
  command: 'node ./scripts/start-backend.cjs',
  url: 'http://127.0.0.1:8000/health',
      reuseExistingServer: true,
      timeout: 120_000,
      env: {
        // Use FS backend for speed and determinism
        PERSISTENCE_BACKEND: 'fs',
        ENABLE_DUAL_WRITE: 'false',
        ENABLE_FS_FALLBACK: 'true',
        // Use performance mode to avoid heavy model paths in tests
        STRATEGY_DETECTION_MODE: 'performance',
        MAX_SENTENCES_FOR_PERFORMANCE: '3',
        // Prefer cached locations; do not hard fail if huggingface caches missing
        HF_HOME: 'c:\\net\\.huggingface-cache',
      },
    },
    {
      // Start frontend (Vite) on a strict port to match baseURL
  command: 'npm run dev -- --port 5173 --strictPort',
  url: 'http://localhost:5173',
      reuseExistingServer: true,
      timeout: 120_000,
      env: {
        VITE_API_BASE_URL: 'http://127.0.0.1:8000',
      },
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
