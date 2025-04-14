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
        <div v-if="vitalModel">
          <DataTable
            :value="filteredVitalData"
            v-if="layout === 'table'"
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

const props = defineProps({
  vitals: Array,
  vitalTypes: Array,
})

const emit = defineEmits(['delete', 'openEdit'])

const vitalModel = ref()
const selectedVitalId = ref(null)
const menu = ref()
const confirm = useConfirm()

const selectedDates = ref(null)

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

const filteredVitalData = computed(() => {
  let filtered
  if (selectedDates.value) {
    if (!selectedDates.value[1]) {
      filtered = props.vitals.filter(
        (vital) =>
          vital.date_recorded >= selectedDates.value[0] && vital.name === vitalModel.value.name,
      )
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

const chartData = computed(() => {
  if (!filteredVitalData.value.length) {
    return {}
  }

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

const toggle = (event, id) => {
  selectedVitalId.value = id
  menu.value.toggle(event)
}

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
      try {
        await api.delete(`/me/healthdata/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}

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
