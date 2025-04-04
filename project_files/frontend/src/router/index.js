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
    }
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
