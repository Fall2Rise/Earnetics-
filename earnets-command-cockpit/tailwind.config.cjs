/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        obsidian: "#050509",
        cockpit: "#070a0f",
        neon: {
          cyan: "#4af2ff",
          magenta: "#ff6ad5",
          violet: "#8b5cf6",
          blue: "#38bdf8",
        },
      },
      boxShadow: {
        glow: "0 0 20px rgba(74, 242, 255, 0.35)",
      },
      borderRadius: {
        hud: "18px",
      },
    },
  },
  plugins: [],
};
