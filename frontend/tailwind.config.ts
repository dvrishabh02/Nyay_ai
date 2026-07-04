import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f4f1ea",
        surface: "#faf8f4",
        ink: "#211f1b",
      },
      fontFamily: {
        serif: ["var(--font-newsreader)", "serif"],
        sans: ["var(--font-hanken)", "system-ui", "sans-serif"],
        devanagari: ["var(--font-devanagari)", "serif"],
      },
      keyframes: {
        nyRise: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "none" },
        },
        nyBlink: {
          "0%, 60%, 100%": { opacity: ".25" },
          "30%": { opacity: "1" },
        },
      },
      animation: {
        "ny-rise": "nyRise .3s ease both",
        "ny-blink": "nyBlink 1.2s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
