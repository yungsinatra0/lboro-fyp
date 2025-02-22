<template>
  <NavBar />

  <div class="min-h-screen bg-surface-0 dark:bg-surface-900">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
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

    <div class="flex flex-col items-center gap-4 p-3 md:p-5">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="allergies.length === 0" class="p-4">
        Nu a fost gasita nici o alergie.
      </div>

      <AllergyCard
        v-else
        v-for="allergy in allergies"
        :key="allergy.id"
        v-bind="allergy"
        @delete="deleteAllergy"
        @open-edit="openEditDialog"
      />
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import AllergyCard from '@/components/allergies/AllergyCard.vue'
import { onMounted, ref } from 'vue'
import api from '../services/api'

const allergies = ref([])
const allergyReactions = ref([])
const allergyAllergens = ref([])
const loading = ref(true)
const error = ref(null)
const displayAddDialog = ref(false)

onMounted(async () => {
    try {
        const response = await api.get('/allergies')
        allergies.value = response.data
        const responseReactions = await api.get('/reactions')
        allergyReactions.value = responseReactions.data.map(reaction => reaction.name)
        const responseAllergens = await api.get('/allergens')
        allergyAllergens.value = responseAllergens.data.map(allergen => allergen.name)
    } catch (error) {
        error.value = error.response.data.message
        loading.value = false
    }
    finally {
        loading.value = false
    }
  
})

const showAddDialog = () => {
  displayAddDialog.value = true
}
</script>
