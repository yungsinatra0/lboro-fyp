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

    <div class="flex-1 p-3 md:p-5 w-full">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="vaccines.length === 0" class="p-4">Nu a fost gasit nici un vaccin.</div>

      <VaccineDataView
        v-else
        :vaccines=vaccines
        @delete="deleteVaccine"
        @open-edit="openEditDialog"
        @show-file="showCertificate"
        class="w-full h-full"
      />
    </div>

    <AddVaccine
      v-if="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addVaccine"
      :display-dialog="displayAddDialog"
    />

    <EditVaccine
      v-if="displayEditDialog"
      @edit="refreshUpdatedVaccine"
      @close="displayEditDialog = false"
      :display-dialog="displayEditDialog"
      :vaccine="editDialogData"
    />

    <ShowCertificate
      v-if="displayCertificateDialog"
      :display-dialog="displayCertificateDialog"
      @close="displayCertificateDialog = false"
      :vaccine-id="vaccineIdForCertificate"
    />
  </div>
</template>

<script setup>
/**
 * @file VaccineView.vue
 * @description This file contains the VaccineView component, which is responsible for displaying and managing the user's vaccines. This is the main view for vaccines, containing other components for adding, editing, viewing vaccines and their certificates.
 */
import NavBar from '@/components/NavBar.vue'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import AddVaccine from '@/components/vaccines/AddVaccine.vue'
import EditVaccine from '@/components/vaccines/EditVaccine.vue'
import ShowCertificate from '@/components/vaccines/ShowCertificate.vue'
import VaccineDataView from '@/components/vaccines/VaccineDataView.vue'

const vaccines = ref([])
const loading = ref(true)
const error = ref(null)

const displayAddDialog = ref(false)
const displayEditDialog = ref(false)
const displayCertificateDialog = ref(false)
const vaccineIdForCertificate = ref(null)
const editDialogData = ref(null)

/**
 * @function onMounted
 * @description This function is called when the component is mounted. It fetches the user's vaccines from the API and sets them to the vaccines ref.
 * It also handles any errors that may occur during the API call.
 */
onMounted(async () => {
  try {
    const response = await api.get('me/vaccines')
    vaccines.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'A aparut o eroare la incarcarea vaccinelor. Te rugam sa incerci mai tarziu.'
  } finally {
    loading.value = false
  }
})

/**
 * @function showAddDialog
 * @description This function is used to show the add vaccine dialog.
 * It sets the displayAddDialog ref to true, which will trigger the dialog to be displayed.
 */
const showAddDialog = () => {
  displayAddDialog.value = true
}

/**
 * @function addVaccine
 * @description This function is used to add a new vaccine to the list of vaccines.
 * It takes the new vaccine object as a parameter and pushes it to the vaccines array.
 * @param {object} vaccine - The new vaccine object to be added.
 */
const addVaccine = (vaccine) => {
  vaccines.value.push(vaccine)
}

/**
 * @function deleteVaccine
 * @description This function is used to delete a vaccine from the list of vaccines.
 * It takes the id of the vaccine as a parameter and removes it from the vaccines array.
 * @param {number} id - The id of the vaccine to be deleted.
 */
const deleteVaccine = (id) => {
  vaccines.value = vaccines.value.filter((vaccine) => vaccine.id !== id)
}

/**
 * @function openEditDialog
 * @description This function is used to open the edit vaccine dialog.
 * It takes the id of the vaccine as a parameter, finds the relevant vaccine object and sets the editDialogData ref to the vaccine object.
 * It also sets the displayEditDialog ref to true, which will trigger the dialog to be displayed.
 * @param {number} id - The id of the vaccine to be edited.
 */
const openEditDialog = (id) => {
  displayEditDialog.value = true
  const vaccine = vaccines.value.find((vaccine) => vaccine.id === id)
  editDialogData.value = vaccine
}

/**
 * @function refreshUpdatedVaccine
 * @description This function is used to refresh the updated vaccine in the list of vaccines.
 * It takes the updated vaccine object as a parameter and updates the relevant vaccine object in the vaccines array.
 * @param {object} vaccine - The updated vaccine object to be refreshed.
 */
const refreshUpdatedVaccine = (vaccine) => {
  const index = vaccines.value.findIndex((v) => v.id === vaccine.id)
  vaccines.value[index] = vaccine
}

/**
 * @function showCertificate
 * @description This function is used to show the certificate dialog for a specific vaccine.
 * It takes the id of the vaccine as a parameter and sets it to the vaccineIdForCertificate ref.
 * It also sets the displayCertificateDialog ref to true, which will trigger the dialog to be displayed.
 * @param {number} id - The id of the vaccine whose certificate is to be shown.
 */
const showCertificate = (id) => {
  displayCertificateDialog.value = true
  vaccineIdForCertificate.value = id
}
</script>
