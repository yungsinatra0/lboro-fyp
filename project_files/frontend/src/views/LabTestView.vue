<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Analize laborator
      </h1>
    </div>

    <!-- Mobile filter section - only visible on small screens -->
    <div class="md:hidden p-3 flex flex-col gap-3">
      <DatePicker
        v-model="selectedDates"
        placeholder="Selecteaza datele"
        selectionMode="range"
        showIcon
        dateFormat="dd/mm/yy"
        class="w-full text-base"
        showButtonBar
      />
      <!-- Global keyword search function -->
      <IconField class="w-full">
        <InputIcon>
          <i class="pi pi-search" />
        </InputIcon>
        <InputText class="w-full" v-model="filters['global'].value" placeholder="Cauta..." />
      </IconField>
    </div>

    <DataTable
      v-model:expandedRows="expandedRows"
      :value="dateFilter"
      dataKey="id"
      :rows="10"
      :rowsPerPageOptions="[5, 8, 10]"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
      currentPageReportTemplate="{first}-{last} din {totalRecords}"
      v-model:filters="filters"
      :globalFilterFields="['name', 'code']"
      removableSort
      breakpoint="768px"
      class="p-datatable-sm"
    >
      <template #header>
        <!-- Desktop filter section - only visible on larger screens -->
        <div class="hidden md:flex justify-end items-center flex-wrap gap-2 mb-2">
          <DatePicker
            v-model="selectedDates"
            placeholder="Selecteaza datele"
            selectionMode="range"
            showIcon
            dateFormat="dd/mm/yy"
            class="text-base"
            showButtonBar
            size="small"
          />
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText size="small" v-model="filters['global'].value" placeholder="Cauta..." />
          </IconField>
        </div>
      </template>

      <!-- Parent table columns for each lab test -->
      <Column expander style="width: 3rem"> </Column>
      <Column field="name" header="Nume" sortable></Column>
      <Column field="code" header="Cod" class="hidden sm:table-cell"></Column>
      <Column header="Rezultatul recent">
        <template #header>
          <div class="flex items-center gap-1">
            <i
              v-tooltip.top="
                'Unitatea folosita poate fi diferita in functie de laboratorul care a efectual analiza.'
              "
              class="pi pi-info-circle text-sm"
            />
          </div>
        </template>
        <template #body="slotProps">
          <span v-if="!slotProps.data.results[0].value"> - </span>
          <template v-else>
            <span> {{ slotProps.data.results[0].value }} </span>
            <div class="text-xs text-gray-400">{{ slotProps.data.results[0].unit }}</div>
          </template>
        </template>
      </Column>
      <Column header="Interval de referinta" class="hidden md:table-cell">
        <template #header>
          <div class="flex items-center gap-1">
            <i
              v-tooltip.top="
                'Intervalele de referinta pot fi diferite in functie de laboratorul care a efectuat analiza.'
              "
              class="pi pi-info-circle text-sm"
            />
          </div>
        </template>
        <template #body="slotProps">
          <span v-if="!slotProps.data.results[0].reference_range"> - </span>
          <template v-else>
            <span> {{ slotProps.data.results[0].reference_range }} </span>
            <div class="text-xs text-gray-400">{{ slotProps.data.results[0].unit }}</div>
          </template>
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
            v-tooltip="'Peste limita normala'"
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
            v-tooltip="'Sub limita normala'"
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
            v-tooltip="'In limitele normale'"
          ></i>
        </template>
      </Column>
      <Column header="Evolutia rezultatelor" class="hidden md:table-cell">
        <template #body="slotProps">
          <template v-if="slotProps.data.results.some((result) => result.is_numeric === true)">
            <Line
              :data="getChartData(slotProps.data.results)"
              :options="chartOptions"
              :width="150"
              :height="50"
            />
          </template>
        </template>
      </Column>

      <!-- Expansion data table for child rows (lab result) for each lab test -->
      <template #expansion="slotProps">
        <div class="p-2 md:p-4">
          <h5 class="text-lg font-medium mb-3">Rezultate pentru {{ slotProps.data.name }}</h5>
          
          <!-- Mobile chart and reference interval display for each lab test (only shown when expanded) -->
          <div
            class="block lg:hidden mb-4"
            v-if="slotProps.data.results.some((result) => result.is_numeric === true)"
          >
            <Line
              :data="getChartData(slotProps.data.results)"
              :options="mobileChartOptions"
              :height="150"
            />
          </div>
          <div class="block md:hidden mb-4" v-if="slotProps.data.results[0].reference_range">
            <div class="p-3 bg-surface-50 dark:bg-surface-800 rounded">
              <div class="text-sm font-medium">Interval de referinta:</div>
              <div>
                {{ slotProps.data.results[0].reference_range }}
                <span class="text-xs text-gray-400">{{ slotProps.data.results[0].unit }}</span>
              </div>
            </div>
          </div>

          <DataTable
            :value="slotProps.data.results"
            dataKey="id"
            responsiveLayout="stack"
            breakpoint="768px"
            class="p-datatable-sm"
            scrollable
            scrollHeight="400px"
          >
          <!-- Lab results columns -->
            <Column field="value" header="Rezultat">
              <template #body="slotProps">
                <span>{{ slotProps.data.value }}</span>
                <span class="text-xs text-gray-400 ml-1">{{ slotProps.data.unit }}</span>
              </template>
            </Column>
            <Column field="unit" header="Unitate" class="hidden md:table-cell"></Column>
            <Column
              field="reference_range"
              header="Interval de referinta"
              class="hidden md:table-cell"
            >
              <template #body="slotProps">
                <span v-if="!slotProps.data.reference_range"> - </span>
                <template v-else>
                  <span> {{ slotProps.data.reference_range }} </span>
                  <span class="text-xs text-gray-400">{{ slotProps.data.unit }}</span>
                </template>
              </template>
            </Column>
            <Column field="method" header="Metoda" class="hidden md:table-cell">
              <template #body="slotProps">
                <span v-if="!slotProps.data.method"> - </span>
                <span v-else>{{ slotProps.data.method }}</span>
              </template>
            </Column>
            <Column field="date_collection" header="Data recoltarii">
              <template #body="slotProps">
                {{ slotProps.data.original_date_collection }}
              </template>
            </Column>
            <Column header="Optiuni">
              <template #body="{ data }">
                <div class="flex flex-row gap-2 justify-start md:justify-end">
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
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </template>

      <!-- Empty section in case no data is passed. Will show the empty message and error if there is -->
      <template #empty>
        <div class="p-4 text-center">
          <i class="pi pi-search text-3xl text-gray-300 dark:text-gray-600 mb-2"></i>
          <p>Nu au fost gasite rezultate care sa corespunda criteriilor de cautare.</p>
        </div>

        <!-- Error message display -->
        <Message v-if="error" severity="error" class="mx-3 md:mx-5 mb-3">
          <template #container>
            <div class="flex items-center justify-between">
              <div>{{ error }}</div>
              <Button icon="pi pi-refresh" severity="secondary" text @click="retryFetch" />
            </div>
          </template>
        </Message>
      </template>

      <!-- Loading indicator -->
      <template #loading>
        <ProgressSpinner v-if="loading" class="mx-auto my-5" />
        <span> Datele se incarca...</span>
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
/**
 * @file LabTestView.vue
 * @description This file contains the LabTestView component, which displays laboratory test results, alongside the recent results, reference intervals, and trends. Also shows a small sparkline chart for each test to show evolution of the results.
 */
import NavBar from '@/components/NavBar.vue'
import { calculateTrend, getChartData } from '@/utils'
import ShowFile from '@/components/medhistory/ShowFile.vue'
import { FilterMatchMode } from '@primevue/core/api'
import { ref, onMounted, computed } from 'vue'
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
const loading = ref(false)
const error = ref(null)
const expandedRows = ref({})
const displayFileDialog = ref(false)
const historyIdForFile = ref(null)
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})
const selectedDates = ref(null)

onMounted(() => {
  fetchLabTests()
})

/**
 * Fetches laboratory test data from the API and handles loading states and error messages
 */
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
  } catch (err) {
    console.error('Error fetching lab tests:', err)
    error.value =
      err.response?.data?.detail || 'Nu s-au putut încărca analizele. Vă rugăm încercați din nou.'
  } finally {
    loading.value = false
  }
}
/**
 * Computes filtered lab tests based on selected date range
 * @returns {Array} Filtered lab test results
 */
const dateFilter = computed(() => {
  let filtered
  if (selectedDates.value) {
    if (!selectedDates.value[1]) {
      filtered = labTests.value.map((test) => {
        return {
          ...test,
          results: test.results.filter((result) => {
            return result.date_collection >= selectedDates.value[0]
          }),
        }
      })
    } else {
      filtered = labTests.value.map((test) => {
        return {
          ...test,
          results: test.results.filter((result) => {
            return (
              result.date_collection >= selectedDates.value[0] &&
              result.date_collection <= selectedDates.value[1]
            )
          }),
        }
      })
    }
  } else {
    return labTests.value
  }

  return filtered.filter((test) => {
    return test.results.length > 0
  })
})

// Chart options for desktop chart
const chartOptions = {
  responsive: false,
  maintainAspectRatio: false,
  scales: {
    y: {
      display: false,
      grid: {
        display: false,
      },
      beginAtZero: false,
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
      enabled: true,
      position: 'nearest',
      yAlign: 'center',
      xAlign: 'center',
    },
  },
}

// Chart options for mobile chart
const mobileChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      display: true,
      grid: {
        display: true,
        color: '#c8c8c833',
      },
      ticks: {
        font: {
          size: 10,
        },
      },
    },
    x: {
      display: true,
      grid: {
        display: false,
      },
      ticks: {
        display: true,
        font: {
          size: 10,
        },
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
}
</script>