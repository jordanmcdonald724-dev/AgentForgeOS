import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import fs from "node:fs";
import path from "node:path";
import { transform } from "esbuild";

export default defineConfig({
  plugins: [
    {
      name: "jsx-in-js-src",
      enforce: "pre",
      async transform(code, id) {
        if (!/\/src\/.*\.js$/.test(id)) return;
        if (!code.includes("<")) return;
        const result = await transform(code, { loader: "jsx", sourcemap: true, sourcefile: id });
        return { code: result.code, map: result.map };
      },
    },
    react(),
    {
      name: "copy-wizard-assets",
      closeBundle() {
        const outDir = path.resolve(process.cwd(), "dist");
        if (!fs.existsSync(outDir)) return;
        for (const name of ["wizard.html", "wizard.css"]) {
          const src = path.resolve(process.cwd(), name);
          const dst = path.resolve(outDir, name);
          if (fs.existsSync(src)) {
            fs.copyFileSync(src, dst);
          }
        }
      },
    },
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "@apps": fileURLToPath(new URL("../apps", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      allow: [fileURLToPath(new URL("..", import.meta.url))],
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
