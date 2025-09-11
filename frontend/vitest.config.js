import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    include: [
      'src/**/*.test.{js,jsx,ts,tsx}',
      'src/**/*.spec.{js,jsx,ts,tsx}',
      'tests/**/*.test.{js,jsx,ts,tsx}',
      'tests/**/*.spec.{js,jsx,ts,tsx}'
    ],
    exclude: [
      'node_modules/**',
      'tests/e2e/**'
    ]
  }
});
