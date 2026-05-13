/** @type {import('tailwindcss').Config} */
export default {
  // darkMode через класс — переключатель темы будет добавлять класс `dark` на <html>
  darkMode: ['selector', '[class*="p-dark"]'],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  // Плагин-мост: подключает CSS-переменные PrimeVue как Tailwind-цвета.
  // Можно будет писать bg-primary-500, text-surface-900 и т.д.
  plugins: [require('tailwindcss-primeui')],
}