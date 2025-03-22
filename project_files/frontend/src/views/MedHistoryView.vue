<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Istoric Medical
      </h1>
      <Button
        label="Adauga un istoric medical nou"
        icon="pi pi-plus"
        class="p-button-outlined mr-2"
        @click="showAddDialog"
      />
    </div>
    <div class="flex flex-col">
      <HistoryTableView
        :history="history"
        @delete="deleteHistory"
        @open-edit="openEditDialog"
      />
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import { ref, onMounted } from 'vue'
import HistoryTableView from '@/components/medhistory/HistoryTableView.vue'
import { parse } from 'date-fns'
import api from '@/services/api'

const history = ref([])

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  try {
    const response = await api.get('/me/medicalhistory')
    history.value = response.data.map((item) => {
      return {
        ...item,
        original_date_consultation: item.date_consultation,
        date_consultation: parse(item.date_consultation, 'dd-MM-yyyy', new Date()),
      }
    })
  } catch (error) {
    console.error(error)
  }
}
</script>
