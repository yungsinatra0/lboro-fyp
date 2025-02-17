<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Vaccinele mele
      </h1>
      <Button
        label="Adauga vaccin"
        icon="pi pi-plus"
        class="p-button-outlined mr-2"
        @click="showAddDialog"
      />
    </div>

    <div class="flex flex-col items-center gap-4 p-3 md:p-5">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="vaccines.length === 0" class="p-4">Nu a fost gasit nici un vaccin.</div>

      <VaccineCard
        v-else
        v-for="vaccine in vaccines"
        :key="vaccine.id"
        :id="vaccine.id"
        :name="vaccine.name"
        :provider="vaccine.provider"
        :date-received="vaccine.date_received"
        @delete="deleteVaccine"
        @edit="updateVaccine"
      />
    </div>
    
    <ConfirmDialog></ConfirmDialog>

    <AddVaccine v-if="displayAddDialog" @close="displayAddDialog = false" @add="addVaccine" :display-dialog="displayAddDialog"/>

  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import VaccineCard from '@/components/VaccineCard.vue'
import Button from 'primevue/button'
import { onMounted, ref } from 'vue'
import AddVaccine from '@/components/AddVaccine.vue'
import api from '@/services/api'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'

const vaccines = ref([])
const loading = ref(true)
const error = ref(null)
const displayAddDialog = ref(false)
const new_vaccine = ref(null)

onMounted(async () => {
  try {
    const response = await api.get('me/vaccines')
    vaccines.value = response.data
  } catch (error) {
    error.value = 'O eroare a aparut la incarcarea vaccinurilor: ' + error.message
  } finally {
    loading.value = false
  }
})

const showAddDialog = () => {
  displayAddDialog.value = true
}

const addVaccine = (vaccine) => {
  console.log('Vaccine received by emit: ', vaccine)
  vaccines.value.push(vaccine)
}

const deleteVaccine = (id) => {
  vaccines.value = vaccines.value.filter((vaccine) => vaccine.id !== id)
}

const updateVaccine = async (id) => {
  try {
    const response = await api.get(`me/vaccines/${id}`)
    new_vaccine.value = response.data
    const index = vaccines.value.findIndex((vaccine) => vaccine.id === id)
    if (index !== -1) {
      vaccines.value[index] = new_vaccine.value
    }
  } catch (error) {
    console.error('Error updating vaccine:', error)
  }
}
</script>
