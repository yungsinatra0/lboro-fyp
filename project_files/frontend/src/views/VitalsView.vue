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
        <template #content>
          <div class="flex flex-row flex-wrap gap-3">
            <Card v-for="type in vitalTypes" :key="type.id" :pt="cardDataStyles">
              <template #title>
                <div class="flex flex-row items-center justify-between">
                  <span> {{ type.name }} </span>
                  <i
                    v-if="vitalsTrends[type.name].trend === 'up'"
                    class="pi pi-arrow-up text-green-500"
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
            <Card :pt="cardDataStyles">
              <template #title>
                <div class="flex flex-row items-center justify-between">
                  <span> BMI </span>
                  <i v-if="bmiTrend.trend === 'up'" class="pi pi-arrow-up text-green-500"></i>
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
        class="h-full w-full md:w-2/3"
        :vital-types="vitalTypes"
        :vitals="vitals"
        @delete="deleteVital"
      />
    </div>

    <AddVital 
    v-if="displayAddDialog" 
    :vital-types="vitalTypes"
    :display-dialog="displayAddDialog"
    @close="displayAddDialog = false"
    @add="addVital" 
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import VitalsHistory from '@/components/vitals/VitalsHistory.vue'
import AddVital from '@/components/vitals/AddVital.vue'
import { ref, onMounted, computed } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import api from '@/services/api'
import { parse, compareDesc } from 'date-fns'

const vitalTypes = ref([])
const vitals = ref([])

onMounted(() => {
  fetchData()
})

const fetchData = async () => {
  try {
    const response = await api.get('/healthdata/types')
    vitalTypes.value = response.data
    const response2 = await api.get('/me/healthdata')
    vitals.value = response2.data
  } catch (error) {
    console.error(error)
  }
}

const displayAddDialog = ref(false)

const showAddDialog = () => {
  displayAddDialog.value = true
}

const deleteVital = (id) => {
  vitals.value = vitals.value.filter((vital) => vital.id !== id)
}

const addVital = (vital) => {
  vitals.value.push(vital)
}

const vitalsTrends = computed(() => {
  const result = {}

  vitalTypes.value.forEach((type) => {
    const matchingVitals = vitals.value.filter((vital) => vital.name === type.name)

    if (!matchingVitals.length) {
      result[type.name] = { value: 'Nu au fost gasit valori', trend: 'stable' }
      return
    }

    const sortedVitals = [...matchingVitals].sort((a, b) => {
      const dateA = parse(a.date_recorded, 'dd-MM-yyyy', new Date())
      const dateB = parse(b.date_recorded, 'dd-MM-yyyy', new Date())
      return compareDesc(dateA, dateB)
    })

    const mostRecent = sortedVitals[0]
    const previous = sortedVitals[1] ? sortedVitals[1] : null

    if (mostRecent.value !== undefined && mostRecent.value !== null) {
      result[type.name] = {
        value: mostRecent.value,
        trend: previous
          ? calculateTrend(parseFloat(mostRecent.value), parseFloat(previous?.value))
          : 'stable',
      }
    } else if (mostRecent.value_systolic && mostRecent.value_diastolic) {
      result[type.name] = {
        value: `${mostRecent.value_systolic}/${mostRecent.value_diastolic}`,
        trend: previous
          ? calculateTrend(parseInt(mostRecent.value_systolic), parseInt(previous?.value_systolic))
          : 'stable',
      }
    } else {
      result[type.name] = { value: 'Nu au fost gasit valori', trend: 'stable' }
    }
  })

  return result
})

const calculateTrend = (current, previous) => {
  if (previous === null) return 'stable'

  const threshold = 0.01
  const percentChange = Math.abs((current - previous) / previous)

  if (percentChange < threshold) return 'stable'
  return current > previous ? 'up' : 'down'
}

const bmiTrend = computed(() => {
  const latestWeight = vitalsTrends.value['Greutate']
  const latestHeight = vitalsTrends.value['Înălțime']

  if (!latestHeight || !latestWeight) return { available: false, value: 0, trend: 'stable' }

  const weight = parseFloat(latestWeight.value)
  const height = parseFloat(latestHeight.value) / 100

  const bmi = Math.round((weight / (height * height)) * 10) / 10

  return {
    available: true,
    value: bmi,
    trend: latestWeight.trend,
  }
})

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
