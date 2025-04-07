<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Analize laborator
      </h1>
    </div>

    <DataTable
      v-model:expandedRows="expandedRows"
      :value="labTests"
      dataKey="id"
      :rows="11"
      paginator
      v-model:filters="filters"
      :globalFilterFields="['name', 'code']"
    >
      <template #header>
        <div class="flex justify-end align-items-center flex-wrap gap-2">
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText size="small" v-model="filters['global'].value" placeholder="Cauta..." />
          </IconField>
        </div>
      </template>
      <Column expander style="width: 5rem"> </Column>
      <Column field="name" header="Nume"></Column>
      <Column field="code" header="Cod"></Column>
      <!-- TODO: Check if recent result is actually recent or needs more processing -->
      <Column header="Rezultatul recent">
        <template #header>
          <i
            v-tooltip.top="
              'Unitatea folosita poate fi diferita in functie de laboratorul care a efectual analiza.'
            "
            class="pi pi-info-circle"
          />
        </template>
        <template #body="slotProps">
          <span v-if="!slotProps.data.results[0].value"> - </span>
          <span v-else
            >{{ slotProps.data.results[0].value }} {{ slotProps.data.results[0].unit }}</span
          >
        </template>
      </Column>
      <Column header="Interval de referinta">
        <template #header>
          <i
            v-tooltip.top="
              'Intervalele de referinta pot fi diferite in functie de laboratorul care a efectuat analiza.'
            "
            class="pi pi-info-circle"
          />
        </template>
        <template #body="slotProps">
          <span v-if="!slotProps.data.results[0].reference_range"> - </span>
          <span v-else
            >{{ slotProps.data.results[0].reference_range }}
            {{ slotProps.data.results[0].unit }}</span
          >
        </template>
      </Column>
      <Column header="Trend">
        <template #body="slotProps">
          <i
            class="pi pi-arrow-up text-red-500"
            v-if="
              calculateTrend(
                slotProps.data.results[0].value,
                slotProps.data.results[0].reference_range,
                slotProps.data.results[0].is_numeric,
              ) === 'up'
            "
          ></i>
          <i
            class="pi pi-arrow-down text-red-500"
            v-else-if="
              calculateTrend(
                slotProps.data.results[0].value,
                slotProps.data.results[0].reference_range,
                slotProps.data.results[0].is_numeric,
              ) === 'down'
            "
          ></i>
          <i
            v-else-if="
              calculateTrend(
                slotProps.data.results[0].value,
                slotProps.data.results[0].reference_range,
                slotProps.data.results[0].is_numeric,
              ) === 'normal'
            "
            class="pi pi-check text-green-500"
          ></i>
        </template>
      </Column>
      <Column header="Evolutia rezultatelor">
        <template #body="slotProps">
          <template v-if="slotProps.data.results.some((result) => result.is_numeric === true)">
            <Line
              :data="getChartData(slotProps.data.results)"
              :options="chartOptions"
              :width="100"
              :height="50"
            />
          </template>
        </template>
      </Column>
      <!-- TODO: Add small graph for trend of lab results values as column -->
      <template #expansion="slotProps">
        <div class="p-4">
          <h5 class="m-0">Rezultate pentru {{ slotProps.data.name }}</h5>
          <DataTable :value="slotProps.data.results" dataKey="id">
            <Column field="value" header="Rezultat"></Column>
            <Column field="unit" header="Unitate"></Column>
            <Column field="reference_range" header="Interval de referinta"></Column>
            <Column field="method" header="Metoda">
              <template #body="slotProps">
                <span v-if="!slotProps.data.method"> - </span>
                <span v-else>{{ slotProps.data.method }}</span>
              </template></Column
            >
            <Column field="date_collection" header="Data recoltarii">
              <template #body="slotProps">
                {{ slotProps.data.original_date_collection }}
              </template>
            </Column>
            <Column class="w-24 !text-end" header="Optiuni">
              <template #body="{ data }">
                <div class="flex flex-row gap-2 justify-end">
                  <Button
                    icon="pi pi-eye"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="
                      () => {
                        displayFileDialog = true
                        historyIdForFile = data.medicalhistory.id
                      }
                    "
                    severity="secondary"
                    v-if="data.medicalhistory.file"
                  >
                  </Button>
                  <!-- <Button
                    icon="pi pi-ellipsis-h"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="(event) => toggle(event, data.id)"
                    severity="secondary"
                  ></Button> -->
                </div>
              </template>
            </Column>
            <!-- <Column field="method" header="Metoda"></Column> -->
          </DataTable>
        </div>
      </template>
    </DataTable>

    <ShowFile
      v-if="displayFileDialog"
      :display-dialog="displayFileDialog"
      @close="displayFileDialog = false"
      :history-id="historyIdForFile"
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import ShowFile from '@/components/medhistory/ShowFile.vue'
import { FilterMatchMode } from '@primevue/core/api'
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { parse } from 'date-fns'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const labTests = ref([])
const expandedRows = ref({})
const displayFileDialog = ref(false)
const historyIdForFile = ref(null)
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})

const chartOptions = {
  responsive: false,
  maintainAspectRatio: false,
  scales: {
    y: {
      display: false,
      grid: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    x: {
      display: true,
      grid: {
        display: false,
      },
      title: {
        display: false,
      },
      ticks: {
        display: false,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
    },
  },
}

onMounted(() => {
  fetchLabTests()
})

const fetchLabTests = async () => {
  try {
    const response = await api.get('/me/labtests')
    labTests.value = response.data.map((test) => ({
      ...test,
      results: test.results.map((result) => ({
        ...result,
        date_collection: parse(result.date_collection, 'dd-MM-yyyy', new Date()),
        original_date_collection: result.date_collection,
      })),
    }))
  } catch (error) {
    console.error('Error fetching lab tests:', error)
  }
}

const calculateTrend = (value, reference_range, is_numeric) => {
  if (!value || !reference_range) return null

  if (is_numeric) {
    value = parseFloat(value)
    if (reference_range.includes('-')) {
      const [min, max] = reference_range.split('-').map(Number)
      if (value < min) return 'down'
      if (value > max) return 'up'
    } else if (reference_range.includes('>')) {
      const min = parseFloat(reference_range.replace('>', ''))
      if (value < min) return 'down'
      return 'normal'
    } else if (reference_range.includes('<')) {
      const max = parseFloat(reference_range.replace('<', ''))
      if (value > max) return 'up'
      return 'normal'
    }
    else {
      let reference = parseFloat(reference_range)
      if (value < reference) return 'down'
      if (value > reference) return 'up'
      return 'normal'

    }
  } else if (is_numeric === false) {
    // TODO: Handle non-numeric values (e.g., positive/negative, normal/abnormal)
    return null
  }
  return 'normal'
}

const getChartData = (results) => {
  const numericResults = results.filter((result) => result.is_numeric === true)
  const labels = numericResults.map((result) => result.original_date_collection)
  const data = numericResults.map((result) => parseFloat(result.value))

  return {
    labels,
    datasets: [
      {
        data,
        borderColor: 'rgba(54, 192, 44)',
        borderWidth: 1,
        pointRadius: 0.5,
      },
    ],
  }
}
</script>
