/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#e8fffb",
          100: "#b9fff2",
          200: "#87f9e5",
          400: "#2dd4bf",
          500: "#0f766e",
          600: "#0b5f59",
          900: "#062826"
        },
        risk: {
          low: "#15803d",
          medium: "#d97706",
          high: "#dc2626"
        }
      },
      boxShadow: {
        soft: "0 24px 50px rgba(2, 6, 23, 0.38)"
      }
    },
  },
  plugins: [],
};
