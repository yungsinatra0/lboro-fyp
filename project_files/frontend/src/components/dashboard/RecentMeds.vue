<template>
  <Card :pt="props.cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Medicamentele recent adaugate</h2>
    </template>
    <template #content>
      <DataTable :value="props.medications" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="dosage" header="Doza" sortable> </Column>
        <Column field="frequency" header="Frecventa" sortable> </Column>
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
    <template #empty>
      <div class="flex flex-col items-center justify-center h-full">
        <i class="pi pi-exclamation-triangle text-4xl text-surface-500 dark:text-surface-400"></i>
        <span class="text-lg text-surface-500 dark:text-surface-400"
          >Nu există date disponibile</span
        >
      </div>
    </template>
  </Card>
</template>

<script setup>
/**
 * @file RecentMeds.vue
 * @description This component displays the recently added medications of the user in a table format.
 */

/**
 * @prop {Array} medications - The recent medications to be displayed in the table.
 * @prop {Object} cardStyles - The styling options for the card component.
 */
const props = defineProps({
  medications: Array,
  cardStyles: Object
})
</script>
