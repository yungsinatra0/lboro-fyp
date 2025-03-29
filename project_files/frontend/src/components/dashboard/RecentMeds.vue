<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Medicamentele recent adaugate</h2>
    </template>
    <template #content>
      <DataTable :value="props.medications" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="dosage" header="Doza" sortable> </Column>
        <Column field="frequency" header="Frecventa" sortable> </Column>
        <Column field="form" header="Forma" sortable>
          <template #body="slotProps">
            <Tag
              :value="slotProps.data.form"
              rounded
              severity="info"
              class="text-sm self-start md:self-auto"
            ></Tag>
          </template>
        </Column>
        <Column field="date_prescribed" header="Prescris" sortable>
          <template #body="slotProps">
            <span> {{ slotProps.data.original_date_prescribed }} </span>
          </template>
        </Column>
        <Column field="duration_days" header="Durata" sortable>
          <template #body="slotProps">
            {{ slotProps.data.duration_days + ' zile' }}
          </template>
        </Column>
      </DataTable>
    </template>
    <template #footer>
      <RouterLink to="/medicamente" class="p-button p-button-text"
        >Vezi toate medicamentele</RouterLink
      >
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
// import ColumnGroup from 'primevue/columngroup' // optional
// import Row from 'primevue/row' // optional

const props = defineProps({
  medications: Array,
})

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
