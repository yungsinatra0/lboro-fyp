import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

// Using computed API instead of options API cause I'm already using it in my other Vue files
export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)

  async function checkAuth() { // Function checks if user is authenticated
    console.log('checkAuth called')
    try {
      const response = await api.get('/me') // This will return the user object if the user is authenticated
      console.log('Auth check response:', response)
      isAuthenticated.value = true
      user.value = response.data.user
    }
    catch(error) {
      console.log('Auth check error:', error)
      isAuthenticated.value = false
      user.value = null
    }
  }

  return { isAuthenticated, user, checkAuth }
})
