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
      meta: {requiresAuth: false}
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: {requiresAuth: false}
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterView,
      meta: {requiresAuth: false}
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardView,
      meta: {requiresAuth: true}
    },
  ],
})

// Navigation guard
router.beforeEach(async (to) => { // can also add from, next as arguments
  const authStore = useAuthStore()
  await authStore.checkAuth() // TODO: Change this sometime later as it can be computationally expensive to call this on every route change

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return { name: 'Login' } // Redirect to login if not authenticated
    }
  }

  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    // Redirect to dashboard if logged in user tries to access login/register
    return { name: 'Dashboard' }
    
  }  
  else {
    return true // Continue to requested route
  }
})

export default router
