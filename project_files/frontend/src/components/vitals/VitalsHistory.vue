<template>
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
              <span v-if="slotProps.data.value">{{ slotProps.data.value }} {{ slotProps.data.unit }}</span>
              <span v-else> {{ slotProps.data.value_systolic }}/{{ slotProps.data.value_diastolic }} {{ slotProps.data.unit }}</span>
            </template>
          </Column>
          <Column field="notes" header="Notite"></Column>
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
</template>

<script setup>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Card from 'primevue/card'
import SelectButton from 'primevue/selectbutton'
import Select from 'primevue/select'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  vitals: Array,
  vitalTypes: Array,
})

const vitalModel = ref()

watch(() => props.vitalTypes, (newTypes) => {
  if (newTypes && newTypes.length > 0 && !vitalModel.value) {
    vitalModel.value = newTypes[0]
  }
}, { immediate: true })

const options = ref(['table', 'graph'])
const layout = ref('table')

const filteredHealthData = computed(() => {
  return vitalModel.value
    ? props.vitals.filter((vital) => vital.name === vitalModel.value.name)
    : 'Selecteaza tipul mai intai'
})

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
