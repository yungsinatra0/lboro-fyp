<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Testele de laborator recent adaugate</h2>
    </template>
    <template #content>
      <DataTable
        :value="props.labresults"
        removableSort
        responsiveLayout="stack"
        breakpoint="768px"
        class="p-datatable-sm"
      >
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="code" header="Cod" sortable> </Column>
        <Column field="value" header="Valoarea">
          <template #body="slotProps">
            <span v-if="!slotProps.data.is_numeric"> {{ slotProps.data.value }} </span>
            <template v-else>
              <span> {{ slotProps.data.value }} </span>
              <div class="text-xs text-gray-400">{{ slotProps.data.unit }}</div>
            </template>
          </template>
        </Column>
        <Column field="reference_range" header="Interval de referinta">
          <template #body="slotProps">
            <span v-if="!slotProps.data.reference_range"> - </span>
            <template v-else>
              <span> {{ slotProps.data.reference_range }} </span>
              <div class="text-xs text-gray-400">{{ slotProps.data.unit }}</div>
            </template>
          </template>
        </Column>
        <Column header="Trend">
          <template #body="slotProps">
            <i
              class="pi pi-arrow-up text-red-500"
              v-if="
                calculateTrend(
                  slotProps.data.value,
                  slotProps.data.reference_range,
                  slotProps.data.is_numeric,
                ) === 'up'
              "
              v-tooltip="'Peste limita normala'"
            ></i>
            <i
              class="pi pi-arrow-down text-red-500"
              v-else-if="
                calculateTrend(
                  slotProps.data.value,
                  slotProps.data.reference_range,
                  slotProps.data.is_numeric,
                ) === 'down'
              "
              v-tooltip="'Sub limita normala'"
            ></i>
            <i
              v-else-if="
                calculateTrend(
                  slotProps.data.value,
                  slotProps.data.reference_range,
                  slotProps.data.is_numeric,
                ) === 'normal'
              "
              class="pi pi-check text-green-500"
              v-tooltip="'In limitele normale'"
            ></i>
          </template>
        </Column>
        <Column field="date_collection" header="Data colectarii">
          <template #body="slotProps">
            <span> {{ slotProps.data.original_date_collection }} </span>
          </template>
        </Column>
      </DataTable>
    </template>
    <template #footer>
      <RouterLink to="/laborator" class="p-button p-button-text"
        >Vezi toate testele de laborator
      </RouterLink>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
// import ColumnGroup from 'primevue/columngroup' // optional
// import Row from 'primevue/row' // optional

const props = defineProps({
  labresults: Array,
})

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
    } else {
      let reference = parseFloat(reference_range)
      if (value < reference) return 'down'
      if (value > reference) return 'up'
      return 'normal'
    }
  } else if (is_numeric === false) {
    // Handle non-numeric values (e.g., positive/negative, normal/abnormal)
    return null
  }
  return 'normal'
}

const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
}
</script>
