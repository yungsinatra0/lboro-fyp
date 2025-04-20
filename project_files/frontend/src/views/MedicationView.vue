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
      :routes="medroutes"
    />
  </div>
</template>

<script setup>
/**
 * @file MedicationView.vue
 * @description This file contains the MedicationView component, which is responsible for displaying and managing the user's medications.
 * This is the main view for medications, containing other components for adding, editing, and viewing medications.
 */
import NavBar from '@/components/NavBar.vue'
import EditMedication from '@/components/medications/EditMedication.vue'
import AddMedication from '@/components/medications/AddMedication.vue'
import api from '../services/api'
import { onMounted, ref } from 'vue'
import MedicationDataView from '@/components/medications/MedicationDataView.vue'

const displayAddDialog = ref(false)
const displayEditDialog = ref(false)
const editDialogData = ref(null)
const medications = ref([])
const medforms = ref([])
const medroutes = ref([])
const loading = ref(true)
const error = ref(null)

/**
 * @function onMounted
 * @description This function is called when the component is mounted. It fetches the user's medications, medication forms,
 * and medication routes from the API and sets them to the relevant refs.
 * It also handles any errors that may occur during the API calls.
 */
onMounted(async () => {
  try {
    const [medicationsResponse, formsResponse, routesResponse] = await Promise.all([
      api.get('/me/medications'),
      api.get('/medications/forms'),
      api.get('/medications/routes')
    ])
    
    medications.value = medicationsResponse.data
    medforms.value = formsResponse.data.map((form) => form.name) // get only the name of the form
    medroutes.value = routesResponse.data.map((route) => route.name) // get only the name of the route
  } catch (err) {
    error.value = err.response?.data?.detail || 'A aparut o eroare la incarcarea medicamentelor. Te rugam sa incerci mai tarziu.'
  } finally {
    loading.value = false
  }
})

/**
 * @function showAddDialog
 * @description This function is used to show the add medication dialog.
 * It sets the displayAddDialog ref to true, which will trigger the dialog to be displayed.
 */
const showAddDialog = () => {
  displayAddDialog.value = true
}

/**
 * @function deleteMedication
 * @description This function is used to delete a medication from the list of medications.
 * It takes the id of the medication as a parameter and removes it from the medications array.
 * @param {number} id - The id of the medication to be deleted.
 */
const deleteMedication = (id) => {
  medications.value = medications.value.filter((medication) => medication.id !== id)
}

/**
 * @function addMedication
 * @description This function is used to add a new medication to the list of medications.
 * It takes the new medication object as a parameter and pushes it to the medications array.
 * @param {object} medication - The new medication object to be added.
 */
const addMedication = (medication) => {
  medications.value.push(medication)
}

/**
 * @function openEditDialog
 * @description This function is used to open the edit medication dialog.
 * It takes the id of the medication as a parameter, finds the relevant medication object and sets the editDialogData ref to the medication object.
 * It also sets the displayEditDialog ref to true, which will trigger the dialog to be displayed.
 * @param {number} id - The id of the medication to be edited.
 */
const openEditDialog = (id) => {
  displayEditDialog.value = true
  const medication = medications.value.find((medication) => medication.id === id)
  editDialogData.value = medication
}

/**
 * @function refreshUpdatedMedication
 * @description This function is used to refresh the updated medication in the list of medications.
 * It takes the updated medication object as a parameter and updates the relevant medication object in the medications array.
 * @param {object} updatedMedication - The updated medication object to be refreshed.
 */
const refreshUpdatedMedication = (updatedMedication) => {
  const index = medications.value.findIndex((medication) => medication.id === updatedMedication.id)
  medications.value[index] = updatedMedication
}
</script>
