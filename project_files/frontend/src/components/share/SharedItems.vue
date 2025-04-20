<template>
  <div class="flex flex-col">
    <div class="flex justify-between items-center mb-6 p-4 bg-gray-50 rounded-lg shadow-sm">
      <div class="flex flex-col">
        <h2 class="text-xl font-semibold text-gray-800 mb-2">Date pacient</h2>
        <div class="flex items-center gap-2">
          <i class="pi pi-user text-primary"></i>
          <span class="font-medium">{{ shareData?.patient.name }}</span>
          <span class="text-gray-500 ml-2">| Data nașterii: {{ shareData?.patient.dob }}</span>
        </div>
      </div>

      <!-- Timer to show how much time is left until link expiration -->
      <div v-if="timer" class="bg-primary bg-opacity-10 py-2 px-4 rounded-full flex items-center">
        <i class="pi pi-clock mr-2 text-primary"></i>
        <span class="font-mono font-medium">
          {{ timer.hours < 10 ? `0${timer.hours}` : timer.hours }}:{{
            timer.minutes < 10 ? `0${timer.minutes}` : timer.minutes
          }}:{{ timer.seconds < 10 ? `0${timer.seconds}` : timer.seconds }}
        </span>
      </div>
    </div>

    <!-- Tab component to show each shared item for each tab -->
    <div class="card">
      <Tabs v-model:value="Object.keys(shareData.items)[0]" v-if="shareData && shareData.items">
        <TabList>
          <Tab v-for="key in Object.keys(shareData.items)" :key="key" :value="key">{{ key }}</Tab>
        </TabList>
        <TabPanels>
          <TabPanel v-for="key in Object.keys(shareData.items)" :key="key" :value="key">
            <!-- Table to show shared records -->
            <DataTable
              v-if="key !== 'Analize de laborator'"
              :value="shareData.items[key]"
              :dataKey="key"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
              paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
              currentPageReportTemplate="{first}-{last} din {totalRecords}"
              v-model:filters="filters"
              :globalFilterFields="['name', 'allergens']"
              removableSort
            >
              <template #header>
                <div class="flex justify-end items-center">
                  <IconField>
                    <InputIcon>
                      <i class="pi pi-search" />
                    </InputIcon>
                    <InputText
                      size="small"
                      v-model="filters['global'].value"
                      placeholder="Cauta..."
                    />
                  </IconField>
                </div>
              </template>
              <Column
                v-for="column in getFilteredColumns(key)"
                :key="column"
                :field="column"
                :header="column"
                :sortable="true"
              >
                <template #body="{ data }">
                  <!-- File/Certificate icons -->
                  <Button
                    v-if="['certificate', 'file'].includes(column) && data[column] === true"
                    icon="pi pi-eye"
                    variant="text"
                    severity="secondary"
                    @click="
                      () => {
                        recordType = key === 'Vaccinuri' ? 'vaccine' : 'medicalhistory'
                        recordId = data['id']
                        displayFile = true
                      }
                    "
                    rounded
                  />

                  <!-- Array items as tags -->
                  <template v-else-if="['allergens', 'reactions'].includes(column)">
                    <Tag
                      v-for="(item, index) in data[column]"
                      :key="index"
                      class="mr-1"
                      severity="info"
                      rounded
                      size="small"
                    >
                      {{ item }}
                    </Tag>
                  </template>

                  <!-- Single value as tag -->
                  <Tag
                    v-else-if="
                      ['route', 'form', 'category', 'subcategory', 'labsubcategory'].includes(
                        column,
                      ) && data[column]
                    "
                    class="mr-1"
                    severity="info"
                    rounded
                    size="small"
                  >
                    {{ data[column] }}
                  </Tag>

                  <!-- Severity value as tag -->
                  <Tag
                    v-else-if="['severity'].includes(column) && data[column]"
                    class="mr-1"
                    :severity="data[column] === 'Severă' ? 'danger' : 'warn'"
                    rounded
                    size="small"
                  >
                    {{ data[column] }}
                  </Tag>

                  <span v-else-if="column.includes('date')">
                    {{ data[`original_${column}`] }}
                  </span>

                  <!-- Regular text value -->
                  <span v-else-if="data[column] !== false">{{ data[column] }}</span>
                </template>
              </Column>
            </DataTable>

            <!-- Table used for lab results only -->
            <DataTable
              v-else-if="key === 'Analize de laborator'"
              :value="shareData.items[key]"
              v-model:expandedRows="expandedRows"
              dataKey="name"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
              paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
              currentPageReportTemplate="{first}-{last} din {totalRecords}"
              v-model:filters="filters"
              :globalFilterFields="['name', 'code']"
            >
              <template #header>
                <div class="flex justify-end items-center">
                  <IconField>
                    <InputIcon>
                      <i class="pi pi-search" />
                    </InputIcon>
                    <InputText
                      size="small"
                      v-model="filters['global'].value"
                      placeholder="Cauta..."
                    />
                  </IconField>
                </div>
              </template>
              <Column expander style="width: 5rem" />
              <Column field="name" header="Nume"> </Column>
              <Column field="code" header="Cod"> </Column>
              <Column header="Rezultatul recent">
                <template #body="slotProps">
                  <span v-if="slotProps.data.results && slotProps.data.results.length">
                    {{ slotProps.data.results[slotProps.data.results.length - 1].value }}
                    <span class="text-xs text-gray-400 ml-1">{{
                      slotProps.data.results[slotProps.data.results.length - 1].unit
                    }}</span>
                  </span>
                  <span v-else> - </span>
                </template>
              </Column>
              <Column header="Interval de referinta">
                <template #body="slotProps">
                  <span v-if="slotProps.data.results && slotProps.data.results.length">
                    {{ slotProps.data.results[slotProps.data.results.length - 1].reference_range }}
                    <span class="text-xs text-gray-400 ml-1">{{
                      slotProps.data.results[slotProps.data.results.length - 1].unit
                    }}</span>
                  </span>
                  <span v-else> - </span>
                </template></Column
              >
              <Column header="Trend">
                <template #body="slotProps">
                  <span v-if="slotProps.data.results && slotProps.data.results.length">
                    <i
                      class="pi pi-arrow-up text-red-500"
                      v-if="
                        calculateTrend(
                          slotProps.data.results[slotProps.data.results.length - 1].value,
                          slotProps.data.results[slotProps.data.results.length - 1].reference_range,
                          slotProps.data.results[slotProps.data.results.length - 1].is_numeric,
                        ) === 'up'
                      "
                      v-tooltip="'Peste limita normala'"
                    ></i>
                    <i
                      class="pi pi-arrow-down text-red-500"
                      v-else-if="
                        calculateTrend(
                          slotProps.data.results[slotProps.data.results.length - 1].value,
                          slotProps.data.results[slotProps.data.results.length - 1].reference_range,
                          slotProps.data.results[slotProps.data.results.length - 1].is_numeric,
                        ) === 'down'
                      "
                      v-tooltip="'Sub limita normala'"
                    ></i>
                    <i
                      v-else
                      class="pi pi-check text-green-500"
                      v-tooltip="'In limitele normale'"
                    ></i>
                  </span>
                </template>
              </Column>
              <Column header="Evolutia rezultatelor">
                <template #body="slotProps">
                  <template
                    v-if="slotProps.data.results.some((result) => result.is_numeric === true)"
                  >
                    <Line
                        :data="getChartData([...slotProps.data.results].reverse())"
                      :options="chartOptions"
                      :width="150"
                      :height="50"
                    />
                  </template>
                </template>
              </Column>

              <!-- Expanded table that shows the results for each test name -->
              <template #expansion="slotProps">
                <div class="p-4">
                  <h2>Detalii pentru {{ slotProps.data.name }}</h2>
                  <DataTable
                    :value="slotProps.data.results"
                    dataKey="id"
                    :paginator="true"
                    :rows="5"
                    :rowsPerPageOptions="[5, 10, 20]"
                  >
                    <Column
                      v-for="column in getFilteredColumnsLabs(slotProps.data.results[0])"
                      :key="column"
                      :field="column"
                      :header="column"
                    >
                      <template #body="slotProps" v-if="column === 'date_collection'">
                        {{ slotProps.data[`original_${column}`] }}
                      </template>
                    </Column>
                    <Column header="file">
                      <template #body="slotProps">
                        <Button
                          v-if="slotProps.data.medicalhistory.file === true"
                          icon="pi pi-eye"
                          variant="text"
                          severity="secondary"
                          @click="showFile('medicalhistory', slotProps.data.medicalhistory.id)"
                          rounded
                        />
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </template>
            </DataTable>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>

    <ShowSharedFile
      v-if="displayFile"
      :display-dialog="displayFile"
      :pin="pin"
      :code="$route.params.code"
      :record-type="recordType"
      :record-id="recordId"
      @close="displayFile = false"
    />
  </div>
</template>

<script setup>
/**
 * @file SharedItems.vue
 * @description This file contains the SharedItems component, which is responsible for displaying the shared items via the share link and handling the file display.
 */
import { ref, onMounted } from 'vue'
import ShowSharedFile from './ShowSharedFile.vue'
import { FilterMatchMode } from '@primevue/core/api'
import { parseISO } from 'date-fns'
import { useTimer } from 'vue-timer-hook'
import { calculateTrend, getChartData } from '@/utils'
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

/**
 * @prop {Object} shareData - the data shared via the share link.
 * @prop {String} pin - the PIN code for accessing the shared data. Used for authorizing the file view requests.
 */
const props = defineProps({
  shareData: Object,
  pin: String,
})

const expandedRows = ref({})
const displayFile = ref(false)
const recordType = ref('')
const recordId = ref('')
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})
const timer = ref(null)

/**
 * @description This function is called when the component is mounted. It checks if the shareData has an expiration time and sets up a timer if it does.
 */
onMounted(() => {
  if (props.shareData.expiration_time) {
    const expirationDate = parseISO(props.shareData.expiration_time)
    timer.value = useTimer(expirationDate)
  }
})

// Chart options for the sparkline charts for lab results
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

/**
 * @function showFile
 * @description This function is used to show the file or certificate associated with a specific record.
 * @param type - The type of the record (e.g., 'vaccine', 'medicalhistory')
 * @param id - The ID of the record to be displayed
 */
const showFile = (type, id) => {
  recordType.value = type
  recordId.value = id
  displayFile.value = true
}

/**
 * @function getFilteredColumns
 * @description This function filters the columns of the non-lab items from data table based on the provided key.
 * @param key - The key of the item to be filtered
 */
const getFilteredColumns = (key) => {
  if (!props.shareData?.items?.[key]?.[0]) return []
  return Object.keys(props.shareData.items[key][0]).filter(
    (col) =>
      !['id', 'date_added', 'normal_range', 'trend'].includes(col) && !col.includes('original'),
  )
}

/**
 * @function getFilteredColumnsLabs
 * @description This function filters the columns of the lab results from data table based on the provided result object.
 * @param result - The result object from the lab result
 */
const getFilteredColumnsLabs = (result) => {
  if (!result) return []
  return Object.keys(result).filter(
    (col) =>
      !['id', 'medicalhistory', 'is_numeric', 'date_added'].includes(col) &&
      !col.includes('original'),
  )
}
</script>
