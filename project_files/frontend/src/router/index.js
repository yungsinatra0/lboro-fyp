import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import LandingView from '@/views/LandingView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(), // Will need to change base URL if not using root
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: LandingView,
      meta: { requiresAuth: false },
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterView,
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard
router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    await authStore.checkAuth() // Check if user is authenticated for protected routes
    if (!authStore.isAuthenticated) {
      return { name: 'Login' } // Redirect to login if not authenticated
    }
  } else if (to.path === '/login' || to.path === '/register') {
    await authStore.checkAuth()
    if (authStore.isAuthenticated) {
      return { name: 'Dashboard' } // Redirect to dashboard if authenticated and going to login or register
    }
  }

  return true // Continue to requested route if no conditions are met (I think the documentation says to return true)
})

export default router
