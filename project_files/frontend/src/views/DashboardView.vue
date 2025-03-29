<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-xl font-bold p-3 md:text-3xl md:p-5 text-surface-900 dark:text-surface-0">
        Bine ai venit, {{ user_data?.data?.name }}!
      </h1>
      <div class="flex flex-col md:flex-row gap-2">
        <Button
          label="Adauga un document nou"
          icon="pi pi-file-plus"
          class="p-button-outlined mr-2"
          @click="showAddDialog"
        />
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
        :medhistory="user_data?.data?.medhistory"
        class="mb-4 md:mb-0 md:h-full"
      />
      <RecentHealthData :vitals="user_data?.data?.vitals" class="mb-4 md:mb-0 md:h-full" />

      <RecentMeds :medications="user_data?.data?.medications" class="mb-4 md:mb-0 md:h-full" />

      <Card class="mb-4 md:mb-0 md:h-full md:flex md:flex-col">
        <template #title>
          <h2 class="text-xl font-bold">Analize laborator</h2>
        </template>
        <template #content>
          <p>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Asperiores ullam maiores et
            illo omnis? Quasi optio qui, soluta adipisci sed deserunt veniam labore atque
            perspiciatis expedita sapiente quae at deleniti.
          </p>
        </template>
      </Card>

      <RecentVaccines :vaccines="user_data?.data?.vaccines" class="mb-4 md:mb-0 md:h-full" />

      <RecentAllergies :allergies="user_data?.data?.allergies" class="mb-4 md:mb-0 md:h-full" />
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import RecentVaccines from '@/components/dashboard/RecentVaccines.vue'
import RecentAllergies from '@/components/dashboard/RecentAllergies.vue'
import RecentMeds from '@/components/dashboard/RecentMeds.vue'
import RecentHealthData from '@/components/dashboard/RecentHealthData.vue'
import RecentMedicalHistory from '@/components/dashboard/RecentMedicalHistory.vue'
import { parse } from 'date-fns'

const user_data = ref()

onMounted(async () => {
  try {
    const response = await api.get('/dashboard')
    console.log(response.data)
    user_data.value = {
      data: {
        id: response.data.id,
        name: response.data.name,
        vitals: response.data.vitals.map((vital) => ({
          ...vital,
          original_date_recorded: vital.date_recorded,
          date_recorded: parse(vital.date_recorded, 'dd-MM-yyyy', new Date()),
        })),
        medications: response.data.medications.map((med) => ({
          ...med,
          original_date_prescribed: med.date_prescribed,
          date_prescribed: parse(med.date_prescribed, 'dd-MM-yyyy', new Date()),
        })),
        vaccines: response.data.vaccines.map((vaccine) => ({
          ...vaccine,
          original_date_received: vaccine.date_received,
          date_received: parse(vaccine.date_received, 'dd-MM-yyyy', new Date()),
        })),
        allergies: response.data.allergies,
        medhistory: response.data.medicalhistory.map((history) => ({
          ...history,
          original_date_consultation: history.date_consultation,
          date_consultation: parse(history.date_consultation, 'dd-MM-yyyy', new Date()),
        })),
      },
    }
  } catch (error) {
    console.error(error)
  }
})
</script>
