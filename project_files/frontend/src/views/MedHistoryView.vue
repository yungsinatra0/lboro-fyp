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
    <div class="flex flex-col p-3 md:p-5 w-full">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="history.length === 0" class="p-4">Nu a fost gasit nici un istoric medical.</div>

      <HistoryTableView
        v-else
        :history="history"
        :categories="categories"
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
      :labsubcategories="labsubcategories"
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
      :labsubcategories="labsubcategories"
      @edit="refreshUpdatedHistory"
      @close="displayEditDialog = false"
    />
  </div>
</template>

<script setup>
/**
 * @file MedHistoryView.vue
 * @description This file contains the MedHistoryView component, which is responsible for displaying and managing the user's medical history.
 * This is the main view for medical history, containing other components for adding, editing, viewing, and deleting medical records.
 */
import NavBar from '@/components/NavBar.vue'
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
const labsubcategories = ref([])
const error = ref(null)
const loading = ref(true)

onMounted(() => {
  fetchData()
})

/**
 * @function fetchData
 * @description Fetches the user's medical history and category data from the API.
 * It also formats the date fields for proper display and handles any errors that may occur.
 */
const fetchData = async () => {
  try {
    const [response, categoriesResponse, subcategoriesResponse, labsubcategoriesResponse] = await Promise.all([
      api.get('/me/medicalhistory'),
      api.get('/medicalcategories'),
      api.get('/medicalsubcategories'),
      api.get('/labsubcategories')
    ])

    history.value = response.data.map((item) => {
      return {
        ...item,
        original_date_consultation: item.date_consultation,
        date_consultation: parse(item.date_consultation, 'dd-MM-yyyy', new Date()),
      }
    })
    labsubcategories.value = labsubcategoriesResponse.data.map((labsubcategory) => labsubcategory.name)
    categories.value = categoriesResponse.data.map((category) => category.name)
    subcategories.value = subcategoriesResponse.data.map((subcategory) => subcategory.name)
  } catch (err) {
    error.value = err.response?.data?.detail || 'A aparut o eroare. Te rugam sa incerci mai tarziu.'
  }
  finally {
    loading.value = false
  }
}

/**
 * @function showAddDialog
 * @description Opens the dialog for adding a new medical history record.
 * It sets the displayAddDialog ref to true, which triggers the dialog to be displayed.
 */
const showAddDialog = () => {
  displayAddDialog.value = true
}

/**
 * @function openEditDialog
 * @description Opens the dialog for editing an existing medical history record.
 * It finds the selected history item by ID and sets it as the data for the edit dialog.
 * @param {number} id - The ID of the medical history record to be edited.
 */
const openEditDialog = (id) => {
  displayEditDialog.value = true
  const selectedHistory = history.value.find((item) => item.id === id)
  editDialogData.value = selectedHistory
}

/**
 * @function addHistory
 * @description Adds a new medical history record to the local data array.
 * This function is called after successfully adding a record via the API.
 * @param {object} visit - The new medical history record to be added.
 */
const addHistory = (visit) => {
  history.value.push(visit)
}

/**
 * @function deleteHistory
 * @description Removes a medical history record from the local data array.
 * This function is called after successfully deleting a record via the API.
 * @param {number} id - The ID of the medical history record to be deleted.
 */
const deleteHistory = (id) => {
  history.value = history.value.filter((item) => item.id !== id)
}

/**
 * @function refreshUpdatedHistory
 * @description Updates a medical history record in the local data array after editing.
 * It finds the record by ID and replaces it with the updated version.
 * @param {object} visit - The updated medical history record.
 */
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

/**
 * @function showFile
 * @description Opens the dialog for viewing an attached file from a medical history record.
 * It sets the ID of the record to view and displays the file dialog.
 * @param {number} id - The ID of the medical history record containing the file to view.
 */
const showFile = (id) => {
  displayFileDialog.value = true
  historyIdForFile.value = id
}
</script>
