<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-xl font-bold p-3 md:text-3xl md:p-5 text-surface-900 dark:text-surface-0">
        Bine ai venit, {{ user_data?.data?.name }}!
      </h1>
      <div class="flex flex-col md:flex-row gap-2">
        <Button
          label="Distribuie codul medicului"
          icon="pi pi-share-alt"
          class="p-button-outlined mr-2"
          @click="showShareDialog"
        />
      </div>
    </div>

    <!-- Loading spinner and error message -->
    <div v-if="loading" class="flex flex-col items-center">
      <ProgressSpinner strokeWidth="4" class="w-12 h-12" />
      <span class="text-lg text-surface-600 dark:text-surface-300">Se încarcă datele...</span>
    </div>

    <div v-else-if="error" class="flex flex-col items-center">
      <Message severity="error" class="w-full md:w-3/4 lg:w-1/2">
        {{ error }}
      </Message>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-[5fr_3fr_3fr] gap-4 mx-5">
      <RecentMedicalHistory
        :medhistory="user_data?.data?.records?.medicalhistory.slice(0, 5)"
        :card-styles="cardStyles"
        class="mb-4 md:mb-0 md:h-full"
      />
      <RecentHealthData :vitals="groupedVitals" class="mb-4 md:mb-0 md:h-full"
      :card-styles="cardStyles" />

      <RecentMeds
        :medications="user_data?.data?.records?.medications.slice(0, 5)"
        :card-styles="cardStyles"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentLabResults
        :labresults="user_data?.data?.records?.labresults.slice(0, 5)"
        :card-styles="cardStyles"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentVaccines
        :vaccines="user_data?.data?.records?.vaccines.slice(0, 5)"
        :card-styles="cardStyles"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentAllergies
        :allergies="user_data?.data?.records?.allergies.slice(0, 5)"
        :card-styles="cardStyles"
        class="mb-4 md:mb-0 md:h-full"
      />
    </div>
  </div>

  <CreateShareLink
    v-if="displayShareDialog"
    @close="displayShareDialog = false"
    :display-dialog="displayShareDialog"
    :records="user_data?.data?.records"
  />
</template>

<script setup>
/**
 * @file DashboardView.vue
 * @description Main dashboard view that displays an overview of the user's health information.
 * Shows recent medical records including medications, vaccines, allergies, lab results,
 * health data, and medical history. Also provides functionality to share medical data.
 */
import NavBar from '@/components/NavBar.vue'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import RecentVaccines from '@/components/dashboard/RecentVaccines.vue'
import RecentAllergies from '@/components/dashboard/RecentAllergies.vue'
import RecentMeds from '@/components/dashboard/RecentMeds.vue'
import RecentHealthData from '@/components/dashboard/RecentHealthData.vue'
import RecentMedicalHistory from '@/components/dashboard/RecentMedicalHistory.vue'
import RecentLabResults from '@/components/dashboard/RecentLabResults.vue'
import CreateShareLink from '@/components/dashboard/CreateShareLink.vue'
import { parseDates, groupCompareHealthdata } from '@/utils'

const user_data = ref()
const groupedVitals = ref([])
const displayShareDialog = ref(false)
const loading = ref(true)
const error = ref(null)

/**
 * Fetches the user's dashboard data from the API when the component is mounted.
 * Processes dates for all record types and groups vital signs with trend indicators.
 * Handles loading state and potential errors from the API.
 */
onMounted(async () => {  
  try {
    const response = await api.get('/dashboard')
    user_data.value = {
      data: {
        id: response.data.id,
        name: response.data.name,
        records: {
          vitals: parseDates(response.data.vitals, 'date_recorded'),
          medications: parseDates(response.data.medications, 'date_prescribed'),
          vaccines: parseDates(response.data.vaccines, 'date_received'),
          allergies: parseDates(response.data.allergies, 'date_diagnosed'),
          medicalhistory: parseDates(response.data.medicalhistory, 'date_consultation'),
          labresults: parseDates(response.data.labresults, 'date_collection'),
        },
      },
    }
    groupedVitals.value = groupCompareHealthdata(user_data.value.data.records?.vitals)
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'A apărut o eroare la încărcarea datelor. Vă rugăm să încercați din nou mai târziu.'
  } finally {
    loading.value = false
  }
})

/**
 * @description Shows the dialog for creating a share link.
 * Sets the displayShareDialog ref to true.
 */
const showShareDialog = () => {
  displayShareDialog.value = true
}

const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
}
</script>
