import { fileURLToPath, URL } from "node:url";
import istanbul from "vite-plugin-istanbul";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    istanbul({
      include: "src/*",
      exclude: ["node_modules", "tests/"],
      extension: [".js", ".ts", ".vue"],
      requireEnv: true,
      cypress: true,
      forceBuildInstrument: false,
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  base: "/",
});
