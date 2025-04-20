import { ref, onMounted } from 'vue'

/**
 * Function to manage the dark mode state of the application. 
 * It initializes the dark mode based on user preference and provides a method to toggle it. 
 * @returns {Object} - An object containing the current dark mode state and a method to toggle it.
 */
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