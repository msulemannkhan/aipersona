import path from "node:path"
import { TanStackRouterVite } from "@tanstack/router-vite-plugin"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
  // Load environment variables from the root .env file
  envDir: "../",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  plugins: [react(), TanStackRouterVite()],
  server: {
    port: 5173,
    host: "0.0.0.0",
    allowedHosts: ["counselor-ai.cc", "www.counselor-ai.cc", "localhost", "127.0.0.1"],
  },
})
