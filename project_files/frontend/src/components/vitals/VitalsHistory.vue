<template>
  <div>
    <Card :pt="cardStyles">
      <template #title>
        <span class="text-xl font-bold p-4"> Valori istorice </span>
        <div class="flex gap-2">
          <Select
            v-model="vitalModel"
            :options="props.vitalTypes"
            optionLabel="name"
            placeholder="Selecteaza tipul"
            class="text-base"
          />
          <SelectButton v-model="layout" :options="options" :allowEmpty="false">
            <template #option="{ option }">
              <i :class="[option === 'table' ? 'pi pi-table' : 'pi pi-chart-bar']" />
            </template>
          </SelectButton>
        </div>
      </template>
      <template #content>
        <div v-if="vitalModel">
          <DataTable :value="filteredHealthData" v-if="layout === 'table'" removableSort>
            <Column field="date_recorded" header="Data adaugarii" sortable></Column>
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
          <div v-else>
            <p>Graph</p>
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
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import SelectButton from 'primevue/selectbutton'
import Select from 'primevue/select'
import Menu from 'primevue/menu'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  vitals: Array,
  vitalTypes: Array,
})

const emit = defineEmits(['delete', 'openEdit'])

const vitalModel = ref()
const selectedVitalId = ref(null)
const menu = ref()
const confirm = useConfirm()

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

const filteredHealthData = computed(() => {
  return vitalModel.value
    ? props.vitals.filter((vital) => vital.name === vitalModel.value.name)
    : 'Selecteaza tipul mai intai'
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
  title: { class: 'flex flex-row justify-between items-center' },
}
</script>
