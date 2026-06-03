/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        graphite: "#1f2937",
        panel: "rgba(31, 41, 55, 0.76)",
        cyan: "#0ea5e9",
        violet: "#6366f1"
      },
      boxShadow: {
        glow: "0 0 32px rgba(34, 211, 238, 0.18)",
        card: "0 20px 70px rgba(0,0,0,0.38)"
      },
      backgroundImage: {
        "radial-grid": "linear-gradient(180deg, #1f2937 0%, #111827 100%)"
      }
    }
  },
  plugins: []
};
