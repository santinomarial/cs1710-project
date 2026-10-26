import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/cs1710-project/",
  // Keep every CSV download as a verifiable file under the project base path.
  build: { assetsInlineLimit: 0 },
});
