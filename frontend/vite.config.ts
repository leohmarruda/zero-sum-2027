import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export default defineConfig({
  plugins: [react()],
  // Single source of truth: repo-root `.env` (not frontend/.env).
  envDir: repoRoot,
  server: {
    port: 5173,
    proxy: {
      // Same-origin /api → FastAPI — avoids CORS preflight in local dev.
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
  },
});
