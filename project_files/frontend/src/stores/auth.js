import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

// Using computed API instead of options API cause I'm already using it in my other Vue files
export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)

  async function checkAuth() { // Function checks if user is authenticated
    try {
      const response = await api.get('/me') // This will return the user object if the user is authenticated
      isAuthenticated.value = true
      user.value = response.data.user
    }
    catch {
      isAuthenticated.value = false
      user.value = null
    }
  }

  return { isAuthenticated, user, checkAuth }
})
