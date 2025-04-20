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
    
    <!-- Loading indicator -->
    <div v-if="loading" class="flex-1 p-5 flex justify-center items-center">
      <ProgressSpinner strokeWidth="4" animationDuration=".5s" />
      <span class="ml-2">Se încarcă datele...</span>
    </div>
    
    <!-- Error message display -->
    <div v-else-if="error" class="p-4 text-red-500">
      {{ error }}
    </div>
    
    <div v-else class="flex flex-col mx-3 md:flex-row md:gap-6 md:mx-5 md:justify-between">
      <Card class="h-full" :pt="cardStyles">
        <template #title> Valori curente </template>
        <!-- Show the arrows for current values whether they fall within the normal range instead -->
        <template #content>
          <div class="grid grid-cols-2 gap-3">
            <Card v-for="type in vitalTypes" :key="type.id" :pt="cardDataStyles" class="w-full">
              <template #title>
                <div class="flex flex-row items-center justify-between">
                  <span> {{ type.name }} </span>
                  <i
                    v-if="vitalsTrends[type.name].trend === 'up'"
                    class="pi pi-arrow-up text-red-500"
                  ></i>
                  <i
                    v-else-if="vitalsTrends[type.name].trend === 'down'"
                    class="pi pi-arrow-down text-red-500"
                  ></i>
                  <i v-else class="pi pi-minus-circle text-gray-500"></i>
                </div>
              </template>
              <template #content> {{ vitalsTrends[type.name].value }} {{ type.unit }} </template>
            </Card>
            <Card :pt="cardDataStyles" class="w-full">
              <template #title>
                <div class="flex flex-row items-center justify-between">
                  <span> BMI </span>
                  <i v-if="bmiTrend.trend === 'up'" class="pi pi-arrow-up text-red-500"></i>
                  <i
                    v-else-if="bmiTrend.trend === 'down'"
                    class="pi pi-arrow-down text-red-500"
                  ></i>
                  <i v-else class="pi pi-minus-circle text-gray-500"></i>
                </div>
              </template>
              <template #content> {{ bmiTrend.value }} </template>
            </Card>
          </div>
        </template>
      </Card>
      <VitalsHistory
        class="h-full w-full md:w-5/6"
        :vital-types="vitalTypes"
        :vitals="vitals"
        @delete="deleteVital"
        @open-edit="openEditDialog"
      />
    </div>

    <AddVital
      v-if="displayAddDialog"
      :vital-types="vitalTypes"
      :display-dialog="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addVital"
    />

    <EditVital
      v-if="displayEditDialog"
      :display-dialog="displayEditDialog"
      @edit="refreshUpdatedVital"
      @close="displayEditDialog = false"
      :vital="editDialogData"
      :vital-types="vitalTypes"
    />
  </div>
</template>

<script setup>
/**
 * @file VitalsView.vue
 * @description This file contains the VitalsView component, which is responsible for displaying and managing the user's vital signs. 
 * It shows current vital values with trend indicators and a history of recorded vitals. Users can add, edit, and delete vital measurements.
 */
import NavBar from '@/components/NavBar.vue'
import VitalsHistory from '@/components/vitals/VitalsHistory.vue'
import AddVital from '@/components/vitals/AddVital.vue'
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import { parse, compareDesc } from 'date-fns'
import EditVital from '@/components/vitals/EditVital.vue'

const vitalTypes = ref([])
const vitals = ref([])
const displayAddDialog = ref(false)
const displayEditDialog = ref(false)
const editDialogData = ref(null)
const loading = ref(true)
const error = ref(null)

/**
 * @function onMounted
 * @description This function is called when the component is mounted. It fetches the vital types and the user's vital records.
 */
onMounted(() => {
  fetchData()
})

/**
 * @function fetchData
 * @description Fetches vital types and user vital data from the API
 * It also handles any errors that may occur during the API calls.
 */
const fetchData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const [typesResponse, vitalsResponse] = await Promise.all([
      api.get('/healthdata/types'),
      api.get('/me/healthdata')
    ])
    
    vitalTypes.value = typesResponse.data
    vitals.value = vitalsResponse.data.map((vital) => {
      return {
        ...vital,
        original_date_recorded: vital.date_recorded,
        date_recorded: parse(vital.date_recorded, 'dd-MM-yyyy', new Date()),
      }
    })
  } catch (error) {
    console.error('Error fetching vital data:', error)
    error.value = error.response?.data?.detail || 'A apărut o eroare la încărcarea datelor. Vă rugăm să încercați din nou.'
  } finally {
    loading.value = false
  }
}

/**
 * @function openEditDialog
 * @description Opens the edit dialog for a specific vital measurement
 * @param {string} id - The ID of the vital record to edit
 */
const openEditDialog = (id) => {
  displayEditDialog.value = true
  const vital = vitals.value.find((vital) => vital.id === id)
  editDialogData.value = vital
}

/**
 * @function refreshUpdatedVital
 * @description Updates a vital record in the local state after it has been edited
 * @param {Object} updatedVital - The updated vital record
 */
const refreshUpdatedVital = (updatedVital) => {
  const index = vitals.value.findIndex((vital) => vital.id === updatedVital.id)
  vitals.value[index] = updatedVital
}

/**
 * @function showAddDialog
 * @description Opens the dialog for adding a new vital measurement
 */
const showAddDialog = () => {
  displayAddDialog.value = true
}

/**
 * @function deleteVital
 * @description Removes a vital record from the local state
 * @param {string} id - The ID of the vital record to delete
 */
const deleteVital = (id) => {
  vitals.value = vitals.value.filter((vital) => vital.id !== id)
}

/**
 * @function addVital
 * @description Adds a new vital record to the local state
 * @param {Object} vital - The new vital record to add
 */
const addVital = (vital) => {
  vitals.value.push(vital)
}

/**
 * @function vitalsTrends
 * @description Computed property that calculates the latest value and trend for each vital type
 * @returns {Object} An object with vital names as keys and objects containing value and trend as values
 */
const vitalsTrends = computed(() => {
  const result = {}

  vitalTypes.value.forEach((type) => {
    const matchingVitals = vitals.value.filter((vital) => vital.name === type.name)

    if (!matchingVitals.length) {
      result[type.name] = { value: 'Nu au fost gasit valori', trend: 'stable' }
      return
    }

    const sortedVitals = [...matchingVitals].sort((a, b) => {
      const dateA = a.date_recorded
      const dateB = b.date_recorded
      return compareDesc(dateA, dateB)
    })

    const mostRecent = sortedVitals[0]

    if (mostRecent.value !== undefined && mostRecent.value !== null) {
      const value = parseFloat(mostRecent.value)
      result[type.name] = {
        value: value,
        trend: type.normal_range ? calculateRangeTrend(value, type.normal_range) : 'stable',
      }
    } else if (mostRecent.value_systolic && mostRecent.value_diastolic) {
      const systolic = parseInt(mostRecent.value_systolic)
      result[type.name] = {
        value: `${systolic}/${mostRecent.value_diastolic}`,
        trend: type.normal_range ? calculateRangeTrend(systolic, type.normal_range) : 'stable',
      }
    } else {
      result[type.name] = { value: 'Nu au fost gasit valori', trend: 'stable' }
    }
  })

  return result
})

/**
 * @function calculateRangeTrend
 * @description Determines if a value is above, below, or within a normal range
 * @param {number} value - The value to check
 * @param {string} range - The normal range as a string (e.g., "70-120" or "70-120 mmHg")
 * @returns {string} 'up' if above range, 'down' if below range, 'stable' if within range
 */
const calculateRangeTrend = (value, range) => {
  if (!range) return 'stable'

  let min = 0
  let max = 0

  if (!range.includes('mmHg')) {
    min = parseFloat(range.split('-')[0].trim())
    max = parseFloat(range.split('-')[1].trim())
  } else {
    min = parseFloat(range.split('-')[0].split('/')[0])
    max = parseFloat(range.split('-')[1].split('/')[0])
  }

  if (value < min) return 'down'
  if (value > max) return 'up'
  return 'stable'
}

/**
 * @function bmiTrend
 * @description Computed property that calculates the BMI based on the latest weight and height measurements
 * @returns {Object} An object with the BMI value and trend
 */
const bmiTrend = computed(() => {
  const latestWeight = vitalsTrends.value['Greutate']
  const latestHeight = vitalsTrends.value['Înălțime']

  if (!latestHeight || !latestWeight) return { available: false, value: 0, trend: 'stable' }

  const weight = parseFloat(latestWeight.value)
  const height = parseFloat(latestHeight.value) / 100

  const bmi = Math.round((weight / (height * height)) * 10) / 10

  // BMI ranges: < 18.5 (underweight), 18.5-24.9 (normal), > 24.9 (overweight)
  const trend = calculateRangeTrend(bmi, '18.5-24.9')

  return {
    available: true,
    value: bmi,
    trend: trend,
  }
})

// Card styles configuration
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

const cardDataStyles = {
  body: { class: 'px-4 py-1 flex flex-col' },
  content: { class: 'flex flex-col' },
  root: {
    class:
      'flex bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700 w-1/3 mb-2',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
  title: { class: 'font-bold text-base text-surface-700 dark:text-surface-0' },
}
</script>
