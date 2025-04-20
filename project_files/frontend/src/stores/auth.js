import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

/**
 * Pinia store for managing authentication state.
 * Handles user authentication status and session verification.
 */
export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)

  async function checkAuth() { // Function checks if user is authenticated
    try {
      await api.get('/me') // This will return the user object if the user is authenticated
      isAuthenticated.value = true // if you get response, then user is authenticated
    }
    catch (error) {
      isAuthenticated.value = false // if you don't get response, then user is not authenticated
      console.error('Error checking authentication:', error)
    }
  }
  return { isAuthenticated, checkAuth }
})
