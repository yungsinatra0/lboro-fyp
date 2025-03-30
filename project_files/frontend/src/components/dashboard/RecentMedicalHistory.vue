<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Istoricul recent adaugat</h2>
    </template>
    <template #content>
      <DataTable :value="props.medhistory" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="doctor_name" header="Doctor" sortable> </Column>
        <Column field="category" header="Categoria">
          <template #body="slotProps">
            <Tag :value="slotProps.data.category" severity="info" rounded class="text-sm self-start md:self-auto" />
          </template>
        </Column>
        <Column header="Subcategoria">
          <template #body="slotProps">
            <Tag v-if="slotProps.data.subcategory" :value="slotProps.data.subcategory" severity="info" rounded class="text-sm self-start md:self-auto" />
            <Tag v-else-if="slotProps.data.labsubcategory" :value="slotProps.data.labsubcategory" severity="info" rounded class="text-sm self-start md:self-auto" />
          </template>
        </Column>
        <Column field="date_consultation" header="Data consult" sortable>
          <template #body="slotProps">
            <span> {{ slotProps.data.original_date_consultation }} </span>
          </template>
        </Column>
      </DataTable>
    </template>
    <template #footer>
      <RouterLink to="/istoric" class="p-button p-button-text">Vezi tot istoricul medical </RouterLink>
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
  medhistory: Array,
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
