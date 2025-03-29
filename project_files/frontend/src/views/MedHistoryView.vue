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
        @show-file="showFile"
      />
    </div>

    <AddHistory
      v-if="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addHistory"
      :display-dialog="displayAddDialog"
      :categories="categories"
      :subcategories="subcategories"
    />

    <ShowFile
      v-if="displayFileDialog"
      :display-dialog="displayFileDialog"
      @close="displayFileDialog = false"
      :history-id="historyIdForFile"
    />

    <EditHistory
      v-if="displayEditDialog"
      :display-dialog="displayEditDialog"
      :medical-history="editDialogData"
      :categories="categories"
      :subcategories="subcategories"
      @edit="refreshUpdatedHistory"
      @close="displayEditDialog = false"
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import { ref, onMounted } from 'vue'
import HistoryTableView from '@/components/medhistory/HistoryTableView.vue'
import AddHistory from '@/components/medhistory/AddHistory.vue'
import ShowFile from '@/components/medhistory/ShowFile.vue'
import EditHistory from '@/components/medhistory/EditHistory.vue'
import { parse } from 'date-fns'
import api from '@/services/api'

const history = ref([])
const displayAddDialog = ref(false)
const displayFileDialog = ref(false)
const displayEditDialog = ref(false)
const editDialogData = ref(null)
const historyIdForFile = ref(null)
const categories = ref([])
const subcategories = ref([])

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
    const categoriesResponse = await api.get('/medicalcategories')
    const subcategoriesResponse = await api.get('/medicalsubcategories')
    categories.value = categoriesResponse.data.map((category) => category.name)
    subcategories.value = subcategoriesResponse.data.map((subcategory) => subcategory.name)
  } catch (error) {
    console.error(error)
  }
}

const showAddDialog = () => {
  displayAddDialog.value = true
}

const openEditDialog = (id) => {
  displayEditDialog.value = true
  const selectedHistory = history.value.find((item) => item.id === id)
  editDialogData.value = selectedHistory
}

const addHistory = (visit) => {
  history.value.push(visit)
}

const deleteHistory = (id) => {
  history.value = history.value.filter((item) => item.id !== id)
}

const refreshUpdatedHistory = (visit) => {
  const index = history.value.findIndex((item) => item.id === visit.id)
  if (index !== -1) {
    history.value[index] = {
      ...visit,
      original_date_consultation: visit.date_consultation,
      date_consultation: parse(visit.date_consultation, 'dd-MM-yyyy', new Date()),
    }
  }
}

const showFile = (id) => {
  displayFileDialog.value = true
  historyIdForFile.value = id
}
</script>
