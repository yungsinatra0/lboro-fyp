<template>
  <NavBar />

  <div class="min-h-screen bg-surface-0 dark:bg-surface-900">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Medicamentele mele
      </h1>
      <Button
        label="Adauga medicament"
        icon="pi pi-plus"
        class="p-button-outlined mr-2"
        @click="showAddDialog"
      />
    </div>

    <div class="flex-1 p-3 md:p-5 w-full">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="medications.length === 0" class="p-4">
        Nu a fost gasit nici un medicament.
      </div>

      <MedicationDataView
        v-else
        :medications="medications"
        @delete="deleteMedication"
        @open-edit="openEditDialog"
        class="w-full h-full"
      />
    </div>

    <ConfirmDialog></ConfirmDialog>

    <AddMedication
      v-if="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addMedication"
      :display-dialog="displayAddDialog"
      :forms="medforms"
      :routes="medroutes"
    />

    <EditMedication
      v-if="displayEditDialog"
      @edit="refreshUpdatedMedication"
      @close="displayEditDialog = false"
      :display-dialog="displayEditDialog"
      :medication="editDialogData"
      :forms="medforms"
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import EditMedication from '@/components/medications/EditMedication.vue'
import AddMedication from '@/components/medications/AddMedication.vue'
import ProgressSpinner from 'primevue/progressspinner'
import api from '../services/api'
import { onMounted, ref } from 'vue'
import ConfirmDialog from 'primevue/confirmdialog'
import MedicationDataView from '@/components/medications/MedicationDataView.vue'

const displayAddDialog = ref(false)
const displayEditDialog = ref(false)
const editDialogData = ref(null)
const medications = ref([])
const medforms = ref([])
const medroutes = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const response = await api.get('/me/medications')
    medications.value = response.data
    const response2 = await api.get('/medications/forms')
    medforms.value = response2.data.map((form) => form.name) // get only the name of the form
    const response3 = await api.get('/medications/routes')
    medroutes.value = response3.data.map((route) => route.name) // get only the name of the route
  } catch (err) {
    error.value = 'A aparut o eroare la incarcarea medicamentelor: ' + err.message
  } finally {
    loading.value = false
  }
})

const showAddDialog = () => {
  displayAddDialog.value = true
}

const deleteMedication = (id) => {
  medications.value = medications.value.filter((medication) => medication.id !== id)
}

const addMedication = (medication) => {
  medications.value.push(medication)
}

const openEditDialog = (id) => {
  displayEditDialog.value = true
  const medication = medications.value.find((medication) => medication.id === id)
  editDialogData.value = medication
}

const refreshUpdatedMedication = (updatedMedication) => {
  const index = medications.value.findIndex((medication) => medication.id === updatedMedication.id)
  medications.value[index] = updatedMedication
}
</script>
