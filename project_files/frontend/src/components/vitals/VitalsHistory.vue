<template>
  <div>
    <Card :pt="cardStyles">
      <template #title>
        <span class="text-xl font-bold p-4"> Valori istorice </span>
        <div class="flex flex-row gap-2">
          <Select
            v-model="vitalModel"
            :options="props.vitalTypes"
            optionLabel="name"
            placeholder="Selecteaza tipul"
            class="text-base"
          />
          <DatePicker
            v-model="selectedDates"
            placeholder="Selecteaza datele"
            selectionMode="range"
            showIcon
            dateFormat="dd/mm/yy"
            class="text-base"
            showButtonBar
          />
          <SelectButton v-model="layout" :options="options" :allowEmpty="false">
            <template #option="{ option }">
              <i :class="[option === 'table' ? 'pi pi-table' : 'pi pi-chart-bar']" />
            </template>
          </SelectButton>
        </div>
      </template>
      <template #content>
        <Message
          v-if="vitalModel && vitalModel.normal_range"
          severity="info"
          icon="pi pi-info-circle"
          class="mb-4"
        >
          <span class="font-bold"> Interval de referinta: </span> {{ vitalModel.normal_range }}
        </Message>
        
        <!-- Error message display -->
        <Message v-if="errorMessage" severity="error" class="mb-4 w-full">
          {{ errorMessage }}
        </Message>
        
        <div v-if="vitalModel">
          <!-- Loading state -->
          <div v-if="isLoading" class="flex justify-center items-center h-[40vh]">
            <ProgressSpinner strokeWidth="4" animationDuration=".5s" />
            <span class="ml-2">Se procesează datele...</span>
          </div>
          
          <DataTable
            :value="filteredVitalData"
            v-else-if="layout === 'table'"
            removableSort
            sortField="date_recorded"
            :sortOrder="-1"
          >
            <Column field="date_recorded" header="Data adaugarii" sortable>
              <template #body="slotProps">
                {{ slotProps.data.original_date_recorded }}
              </template></Column
            >
            <Column field="value" header="Valoarea" sortable>
              <template #body="slotProps">
                <span v-if="slotProps.data.value"
                  >{{ slotProps.data.value }} {{ slotProps.data.unit }}</span
                >
                <span v-else>
                  {{ slotProps.data.value_systolic }}/{{ slotProps.data.value_diastolic }}
                  {{ slotProps.data.unit }}</span
                >
              </template>
            </Column>
            <Column field="notes" header="Notite"></Column>
            <Column class="w-24 !text-end">
              <template #body="{ data }">
                <Button
                  icon="pi pi-ellipsis-h"
                  @click="(event) => toggle(event, data.id)"
                  severity="secondary"
                ></Button>
              </template>
            </Column>
          </DataTable>
          <div v-else class="h-[40vh] md:h-[50vh] relative">
            <Line :data="chartData" :options="chartOptions" />
          </div>
        </div>
        <div v-else>
          <h2>Selecteaza tipul mai intai</h2>
        </div>
      </template>
    </Card>

    <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />

    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup>
/**
 * @file VitalsHistory.vue
 * @description Component for displaying a history of vital sign measurements. It provides both table and graph views
 * with filtering options by vital type and date range. Users can also edit or delete vital records.
 */
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'
import { ref, computed, watch } from 'vue'
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
import Message from 'primevue/message'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

/**
 * @prop {Array} vitals - Array of vital sign measurements
 * @prop {Array} vitalTypes - Array of available vital sign types
 */
const props = defineProps({
  vitals: Array,
  vitalTypes: Array,
})

/**
 * @emit {Function} delete - Emits when a vital record is deleted with the ID of the deleted record
 * @emit {Function} openEdit - Emits when a user wants to edit a vital record with the ID of the record to edit
 */
const emit = defineEmits(['delete', 'openEdit'])

const vitalModel = ref()
const selectedVitalId = ref(null)
const menu = ref()
const confirm = useConfirm()
const selectedDates = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

/**
 * @description Watch for changes in vitalTypes prop and set the default vitalModel
 * if it's not already set and there are types available
 */
watch(
  () => props.vitalTypes,
  (newTypes) => {
    if (newTypes && newTypes.length > 0 && !vitalModel.value) {
      vitalModel.value = newTypes[0]
    }
  },
  { immediate: true },
)

const options = ref(['table', 'graph'])
const layout = ref('table')

/**
 * @description Computed property that filters vital data based on selected type and date range
 * @returns {Array} Filtered and sorted vital data
 */
const filteredVitalData = computed(() => {
  let filtered
  if (selectedDates.value) {
    // Check if selected dates is only one date
    if (!selectedDates.value[1]) {
      filtered = props.vitals.filter(
        (vital) =>
          vital.date_recorded >= selectedDates.value[0] && vital.name === vitalModel.value.name,
      )
      // Both selected dates are present
    } else if (selectedDates.value[0] && selectedDates.value[1]) {
      filtered = props.vitals.filter(
        (vital) =>
          vital.date_recorded >= selectedDates.value[0] &&
          vital.date_recorded <= selectedDates.value[1] &&
          vital.name === vitalModel.value.name,
      )
    }
  } else {
    filtered = vitalModel.value
      ? props.vitals.filter((vital) => vital.name === vitalModel.value.name)
      : []
  }

  return [...filtered].reverse()
})

/**
 * @description Configuration options for the chart display
 */
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        filter: (item) => item.text !== 'none',
      },
    },
  },
}

/**
 * @description Computed property that prepares chart data based on filtered vital data
 * @returns {Object} Chart data configuration
 */
const chartData = computed(() => {
  if (!filteredVitalData.value.length) {
    return {}
  }

  // Check if the vital model is compound (e.g., blood pressure)
  if (vitalModel.value.is_compound) {
    return {
      labels: filteredVitalData.value.map((vital) => vital.original_date_recorded),
      datasets: [
        {
          label: `Tensiunea arteriala sistolica`,
          data: filteredVitalData.value.map((vital) => vital.value_systolic),
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.5,
          pointRadius: 5,
        },
        {
          label: `Tensiunea arteriala diastolica`,
          data: filteredVitalData.value.map((vital) => vital.value_diastolic),
          fill: false,
          borderColor: 'rgb(192, 75, 75)',
          tension: 0.5,
          pointRadius: 5,
        },
        ...(vitalModel.value.normal_range
          ? [
              // Removing labels for normal range lines so they don't crowd the legend
              {
                label: 'none',
                showLine: true,
                data: filteredVitalData.value.map(() =>
                  parseInt(vitalModel.value.normal_range.split('-')[0].split('/')[0]),
                ),
                fill: false,
                borderColor: 'rgba(75, 192, 192, 0.6)',
                borderDash: [5, 5],
                tension: 0.5,
                pointRadius: 0,
              },
              {
                label: 'none',
                showLine: true,
                data: filteredVitalData.value.map(() =>
                  parseInt(vitalModel.value.normal_range.split('-')[1].split('/')[0]),
                ),
                fill: false,
                borderColor: 'rgba(75, 192, 192, 0.6)',
                borderDash: [5, 5],
                tension: 0.5,
                pointRadius: 0,
              },
              {
                label: 'none',
                showLine: true,
                data: filteredVitalData.value.map(() =>
                  parseInt(vitalModel.value.normal_range.split('-')[0].split('/')[1]),
                ),
                fill: false,
                borderColor: 'rgba(192, 75, 75, 0.6)',
                borderDash: [5, 5],
                tension: 0.5,
                pointRadius: 0,
              },
              {
                label: 'none',
                showLine: true,
                data: filteredVitalData.value.map(() =>
                  parseInt(vitalModel.value.normal_range.split('-')[1].split('/')[1]),
                ),
                fill: false,
                borderColor: 'rgba(192, 75, 75, 0.6)',
                borderDash: [5, 5],
                tension: 0.5,
                pointRadius: 0,
              },
            ]
          : []),
      ],
    }
  }

  return {
    labels: filteredVitalData.value.map((vital) => vital.original_date_recorded),
    datasets: [
      {
        label: `Valoare, in ${vitalModel.value.unit}`,
        data: filteredVitalData.value.map((vital) => parseFloat(vital.value)),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.5,
        pointRadius: 5,
      },
      ...(vitalModel.value.normal_range
        ? [
            {
              label: 'none',
              showLine: true,
              data: filteredVitalData.value.map(() =>
                parseFloat(vitalModel.value.normal_range.split('-')[0]),
              ),
              fill: false,
              borderColor: 'rgba(128, 128, 128, 0.6)',
              borderDash: [5, 5],
              tension: 0.5,
              pointRadius: 0,
            },
            {
              label: 'none',
              showLine: true,
              data: filteredVitalData.value.map(() =>
                parseFloat(vitalModel.value.normal_range.split('-')[1]),
              ),
              fill: false,
              borderColor: 'rgba(128, 128, 128, 0.6)',
              borderDash: [5, 5],
              tension: 0.5,
              pointRadius: 0,
            },
          ]
        : []),
    ],
  }
})

/**
 * @description Toggles the context menu for a vital record
 * @param {Event} event - The click event
 * @param {string} id - The ID of the vital record
 */
const toggle = (event, id) => {
  selectedVitalId.value = id
  menu.value.toggle(event)
}

/**
 * @description Menu items configuration for the context menu
 */
const menuItems = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          if (selectedVitalId.value) {
            emit('openEdit', selectedVitalId.value)
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedVitalId.value) {
            confirmDelete(event, selectedVitalId.value)
          }
        },
      },
    ],
  },
])

/**
 * @description Shows a confirmation dialog for deleting a vital record
 * @param {Event} event - The click event
 * @param {string} id - The ID of the vital record to delete
 */
const confirmDelete = (event, id) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Esti sigur ca vrei sa stergi acest semn vital?',
    header: 'Confirmare stergere',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Sterge',
      severity: 'danger',
    },
    accept: async () => {
      isLoading.value = true
      errorMessage.value = ''
      
      try {
        await api.delete(`/me/healthdata/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error('Error deleting vital sign:', error)
        errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la ștergerea semnului vital. Vă rugăm să încercați din nou.'
      } finally {
        isLoading.value = false
      }
    },
    reject: () => {},
  })
}

// Card styling configuration
const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
  title: { class: 'flex flex-col md:flex-row justify-between items-center' },
}
</script>
