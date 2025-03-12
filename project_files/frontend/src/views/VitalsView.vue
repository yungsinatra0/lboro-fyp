<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Semne vitale
      </h1>
      <Button
        label="Adauga semn vital nou"
        icon="pi pi-plus"
        class="p-button-outlined mr-2"
        @click="showAddDialog"
      />
    </div>
    <div class="flex flex-col mx-3 md:flex-row md:gap-6 md:mx-5 md:justify-between">
      <Card class="h-full" :pt="cardStyles">
        <template #title> Valori curente </template>
        <template #content> </template>
      </Card>
      <VitalsHistory class="h-full w-full md:w-2/3" :vital-types="healthTypes.data" :vitals="vitals.data" />
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import VitalsHistory from '@/components/vitals/VitalsHistory.vue'
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import api from '@/services/api'

const healthTypes = ref([])
const vitals = ref([])

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  try {
    healthTypes.value = await api.get('/healthdata/types')
    vitals.value = await api.get('/me/healthdata')
  } catch (error) {
    console.error(error)
  }
}

const displayAddDialog = ref(false)

const showAddDialog = () => {
  displayAddDialog.value = true
}

const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700 w-full md:w-1/3 mb-4 md:mb-0',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
  title: { class: 'text-xl font-bold p-4' },
}
</script>
