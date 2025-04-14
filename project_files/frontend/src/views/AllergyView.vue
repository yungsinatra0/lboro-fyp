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

onMounted(async () => {
  try {
    const response = await api.get('/me/allergies')
    allergies.value = response.data
    const responseReactions = await api.get('/reactions')
    allergyReactions.value = responseReactions.data.map((reaction) => reaction.name)
    const responseAllergens = await api.get('/allergens')
    allergyAllergens.value = responseAllergens.data.map((allergen) => allergen.name)
    const responseSeverities = await api.get('/severities')
    allergySeverities.value = responseSeverities.data.map((severity) => severity.name)
  } catch (err) {
    error.value = err.response.data.message
    loading.value = false
  } finally {
    loading.value = false
  }
})

const showAddDialog = () => {
  displayAddDialog.value = true
}

const deleteAllergy = (id) => {
  allergies.value = allergies.value.filter((allergy) => allergy.id !== id)
}

const openEditDialog = (id) => {
  displayEditDialog.value = true
  const allergy = allergies.value.find((allergy) => allergy.id === id)
  editDialogData.value = allergy
}

const addAllergy = (allergy) => {
  allergies.value.push(allergy)
}

const refreshUpdatedAllergy = (updatedAllergy) => {
  const index = allergies.value.findIndex((allergy) => allergy.id === updatedAllergy.id)
  allergies.value[index] = updatedAllergy
}
</script>
