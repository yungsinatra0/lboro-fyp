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
  console.log('Navigation guard triggered for route:', to.name)
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    console.log('Checking auth for:', to.name)
    await authStore.checkAuth() // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      return { name: 'Login' } // Redirect to login if not authenticated
    }
  } else if (to.path === '/login' || to.path === '/register') {
    console.log("I'm in the login/register page, checking if user is already authed")
    await authStore.checkAuth()
    if (authStore.isAuthenticated) {
      return { name: 'Dashboard' } // Redirect to dashboard if authenticated
    }
    console.log("User is not authenticated, continuing to login/register page")
  }

  return true // Continue to requested route
})

export default router
