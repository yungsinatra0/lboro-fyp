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

    <div class="grid grid-cols-1 md:grid-cols-[5fr_3fr_3fr] gap-4 mx-5">
      <RecentMedicalHistory
        :medhistory="user_data?.data?.records?.medhistory.slice(0, 5)"
        class="mb-4 md:mb-0 md:h-full"
      />
      <RecentHealthData :vitals="groupedVitals" class="mb-4 md:mb-0 md:h-full" />

      <RecentMeds
        :medications="user_data?.data?.records?.medications.slice(0, 5)"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentLabResults
        :labresults="user_data?.data?.records?.labresults.slice(0, 5)"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentVaccines
        :vaccines="user_data?.data?.records?.vaccines.slice(0, 5)"
        class="mb-4 md:mb-0 md:h-full"
      />

      <RecentAllergies
        :allergies="user_data?.data?.records?.allergies.slice(0, 5)"
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
          medhistory: parseDates(response.data.medicalhistory, 'date_consultation'),
          labresults: parseDates(response.data.labresults, 'date_collection'),
        },
      },
    }
    groupedVitals.value = groupCompareHealthdata(user_data.value.data.records?.vitals)
  } catch (error) {
    console.error(error)
  }
})

const showShareDialog = () => {
  displayShareDialog.value = true
}
</script>
