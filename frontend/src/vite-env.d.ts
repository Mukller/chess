/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Author: Anton Petnitsky
// GitHub: https://github.com/Mukller/chess
// Last modified: 2026-05-16 21:57:06 +0300
