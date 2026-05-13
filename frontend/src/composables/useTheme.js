import { ref, watch } from 'vue'

const STORAGE_KEY = 'freight-theme'
const stored = localStorage.getItem(STORAGE_KEY)
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
const isDark = ref(stored ? stored === 'dark' : prefersDark)

function apply(dark) {
  document.documentElement.classList.toggle('p-dark', dark)
  document.documentElement.classList.toggle('dark', dark)
}

apply(isDark.value)
watch(isDark, (v) => {
  apply(v)
  localStorage.setItem(STORAGE_KEY, v ? 'dark' : 'light')
})

export function useTheme() {
  return {
    isDark,
    toggle: () => (isDark.value = !isDark.value),
  }
}