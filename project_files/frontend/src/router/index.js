import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import LandingView from '@/views/LandingView.vue'

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
    }
  ],
})

// Navigation guard
router.beforeEach((to) => { // can also add from, next as arguments
  const token = localStorage.getItem('token')
  // TODO: Add a case for non-existing route name
  if (to.meta.requiresAuth && !token) {
    // Redirect to login if trying to access protected route
    return { name: 'Login' }

  } else if (token && (to.path === '/login' || to.path === '/register' || to.path === '/')) {
    // Redirect to dashboard if logged in user tries to access login/register or landing page
    return { name: 'Dashboard' }
    
  }  
  else {
    return true // Continue to requested route
  }
})

export default router
