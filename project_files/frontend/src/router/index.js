import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import LandingView from '@/views/LandingView.vue'
import { useAuthStore } from '../stores/auth'
import VaccineView from '@/views/VaccineView.vue'
import MedicationView from '@/views/MedicationView.vue'
import AllergyView from '@/views/AllergyView.vue'
import ProfileView from '@/views/ProfileView.vue'
import VitalsView from '@/views/VitalsView.vue'
import MedHistoryView from '@/views/MedHistoryView.vue'
import LabTestView from '@/views/LabTestView.vue'
import ShareView from '@/views/ShareView.vue'

/**
 * Vue Router configuration for the application.
 * It defines the routes, their respective components and whether authentication is required to access the specific routes.
 */
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
    {
      path: '/vaccine',
      name: 'Vaccine',
      component: VaccineView,
      meta: { requiresAuth: true },
    },
    {
      path: '/medicamente',
      name: 'Medicamente',
      component: MedicationView,
      meta: { requiresAuth: true },
    },
    {
      path: '/alergii',
      name: 'Alergii',
      component: AllergyView,
      meta: { requiresAuth: true },
    },
    {
      path: '/profil',
      name: 'Profil',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/vitale',
      name: 'Vitale',
      component: VitalsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/istoric',
      name: 'Istoric',
      component: MedHistoryView,
      meta: { requiresAuth: true },
    },
    {
      path: '/laborator',
      name: 'Test Laborator',
      component: LabTestView,
      meta: { requiresAuth: true },
    },
    {
      path: '/share/:code',
      name: 'Share',
      component: ShareView,
      meta: { requiresAuth: false },
    },
  ],
})

/**
 * Navigation guard to check authentication status before each route change.
 * It redirects to the login page if the user is not authenticated and tries to access a protected route.
 * It also redirects authenticated users away from the login and register pages, to avoid circular login loops.
 * @param {Object} to - The target route object being navigated to. Can also use from to get the current route.
 * @returns {Object|boolean} - Returns a route object to redirect to or true to continue navigation.
 */
router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  // Check authentication status before each route change
  await authStore.checkAuth() 

  // If the route requires authentication, check if the user is authenticated
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return { name: 'Login' } // Redirect to login if not authenticated
    }
  } else if (authStore.isAuthenticated && to.name !== 'Share') {
    // If user is authenticated and trying to access login or register pages
    if (to.name === 'Login' || to.name === 'Register') {
      return { name: 'Dashboard' } // Redirect to dashboard
    }
  }

  return true // Continue to requested route if no conditions are met
})

export default router
