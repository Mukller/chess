import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3000,
  },
  preview: {
    host: "0.0.0.0",
    port: 80,
  },
  build: {
    sourcemap: false,
    outDir: "dist",
  },
});

// Author: Anton Petnitsky
// GitHub: https://github.com/Mukller/chess
// Last modified: 2026-05-16 21:57:06 +0300
