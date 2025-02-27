<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Vaccinurile recent adaugate</h2>
    </template>
    <template #content>
      <DataTable :value="props.vaccines" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="provider" header="Furnizorul" sortable> </Column>
        <Column field="date_received" header="Data primirii" sortable> </Column>
      </DataTable>
    </template>
    <template #footer>
        <RouterLink to="/vaccine" class="p-button p-button-text"
          >Vezi toate vaccinurile</RouterLink
        >
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
  vaccines: Array,
})

const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
  footer : { class: 'flex mt-auto justify-center items-center' },
}
</script>
