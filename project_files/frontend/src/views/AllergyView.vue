<template>
  <NavBar />

  <div class="min-h-screen bg-surface-0 dark:bg-surface-900">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Alergiile mele
      </h1>
      <Button
        label="Adauga alergie"
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

      <div v-else-if="allergies.length === 0" class="p-4">Nu a fost gasita nici o alergie.</div>

        <AllergyDataView  
          v-else
          :allergies="allergies"
          :allergens="allergyAllergens"
          :reactions="allergyReactions"
          :severities="allergySeverities"
          @delete="deleteAllergy"
          @open-edit="openEditDialog"
          class="w-full h-full"
        />
    </div>

    <AddAllergy
      v-if="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addAllergy"
      :display-dialog="displayAddDialog"
      :reactions="allergyReactions"
      :allergens="allergyAllergens"
      :severities="allergySeverities"
    />

    <EditAllergy
      v-if="displayEditDialog"
      @edit="refreshUpdatedAllergy"
      @close="displayEditDialog = false"
      :display-dialog="displayEditDialog"
      :allergy="editDialogData"
      :reactions="allergyReactions"
      :allergens="allergyAllergens"
      :severities="allergySeverities"
    />
  </div>
</template>

<script setup>
/**
 * @file AllergyView.vue
 * @description This file contains the AllergyView component, which is responsible for displaying and managing the user's allergies. This is the main view for allergies, containing other components for adding, editing, and viewing allergies.
 */
import NavBar from '@/components/NavBar.vue'
import AllergyDataView from '@/components/allergies/AllergyDataView.vue'
import AddAllergy from '@/components/allergies/AddAllergy.vue'
import EditAllergy from '@/components/allergies/EditAllergy.vue'
import { onMounted, ref } from 'vue'
import api from '@/services/api'

const allergies = ref([])
const allergyReactions = ref([])
const allergyAllergens = ref([])
const allergySeverities = ref([])
const loading = ref(true)
const error = ref(null)
const displayAddDialog = ref(false)
const editDialogData = ref(null)
const displayEditDialog = ref(false)

/**
 * @function onMounted
 * @description This function is called when the component is mounted. It fetches the user's allergies, reactions, allergens, and severities from the API and sets them to the relevant refs.
 * It also handles any errors that may occur during the API calls.
 */
onMounted(async () => {
  try {
    const [response, responseReactions, responseAllergens, responseSeverities] = await Promise.all([
      api.get('/me/allergies'),
      api.get('/reactions'),
      api.get('/allergens'),
      api.get('/severities')
    ])
    allergies.value = response.data
    allergyReactions.value = responseReactions.data.map((reaction) => reaction.name)
    allergyAllergens.value = responseAllergens.data.map((allergen) => allergen.name)
    allergySeverities.value = responseSeverities.data.map((severity) => severity.name)
  } catch (err) {
    error.value = err.response?.data?.detail || 'A aparut o eroare. Te rugam sa incerci mai tarziu.'
  } finally {
    loading.value = false
  }
})

/**
 * @function showAddDialog
 * @description This function is used to show the add allergy dialog.
 * It sets the displayAddDialog ref to true, which will trigger the dialog to be displayed.
 */
const showAddDialog = () => {
  displayAddDialog.value = true
}

/**
 * @function deleteAllergy
 * @description This function is used to delete an allergy from the list of allergies.
 * It takes the id of the allergy as a parameter and removes it from the allergies array.
 * @param {number} id - The id of the allergy to be deleted.
 */
const deleteAllergy = (id) => {
  allergies.value = allergies.value.filter((allergy) => allergy.id !== id)
}

/**
 * @function openEditDialog
 * @description This function is used to open the edit allergy dialog.
 * It takes the id of the allergy as a parameter, finds the relevant allergy object and sets the editDialogData ref to the allergy object.
 * It also sets the displayEditDialog ref to true, which will trigger the dialog to be displayed.
 * @param {number} id - The id of the allergy to be edited.
 */
const openEditDialog = (id) => {
  displayEditDialog.value = true
  const allergy = allergies.value.find((allergy) => allergy.id === id)
  editDialogData.value = allergy
}

/**
  * @function addAllergy
  * @description This function is used to add a new allergy to the list of allergies.
  * It takes the new allergy object as a parameter and pushes it to the allergies array.
  * @param {object} allergy - The new allergy object to be added.
  */
const addAllergy = (allergy) => {
  allergies.value.push(allergy)
}

/**
  * @function refreshUpdatedAllergy
  * @description This function is used to refresh the updated allergy in the list of allergies.
  * It takes the updated allergy object as a parameter and updates the relevant allergy object in the allergies array.
  * @param {object} updatedAllergy - The updated allergy object to be refreshed.
  */
const refreshUpdatedAllergy = (updatedAllergy) => {
  const index = allergies.value.findIndex((allergy) => allergy.id === updatedAllergy.id)
  allergies.value[index] = updatedAllergy
}
</script>
