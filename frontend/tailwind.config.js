import flowbitePlugin from "flowbite/plugin";

export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "node_modules/flowbite-vue/**/*.{js,jsx,ts,tsx,vue}",
    "node_modules/flowbite/**/*.{js,jsx,ts,tsx}",
  ],
  plugins: [flowbitePlugin],
  theme: {
    extend: {
      backgroundImage: {
        "predictcr-logo": "url('http://localhost:5173/logo.png')",
      },
    },
  },
};
