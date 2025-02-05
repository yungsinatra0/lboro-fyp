import { ref, onMounted } from 'vue'

export function useDarkMode() {
  const isDarkMode = ref(false)

  // Initialize dark mode state
  const initializeTheme = () => {
    isDarkMode.value = 
      localStorage.theme === 'dark' || 
      (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
    
    document.documentElement.classList.toggle('app-dark', isDarkMode.value)
  }

  // Toggle dark mode
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.theme = isDarkMode.value ? 'dark' : 'light'
    document.documentElement.classList.toggle('app-dark', isDarkMode.value)
  }
  
  onMounted(() => {
    initializeTheme()
  })

  return {
    isDarkMode,
    toggleDarkMode,

  }
}