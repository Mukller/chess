/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        board: {
          light: "#f0d9b5",
          dark: "#b58863",
        },
        accent: {
          DEFAULT: "var(--tg-theme-button-color, #2481cc)",
          fg: "var(--tg-theme-button-text-color, #ffffff)",
        },
        surface: {
          DEFAULT: "var(--tg-theme-bg-color, #ffffff)",
          alt: "var(--tg-theme-secondary-bg-color, #f4f4f5)",
          hint: "var(--tg-theme-hint-color, #707579)",
          text: "var(--tg-theme-text-color, #111111)",
        },
      },
    },
  },
  plugins: [],
};
