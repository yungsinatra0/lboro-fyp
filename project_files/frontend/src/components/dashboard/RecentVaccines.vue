<template>
  <Card :pt="props.cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Vaccinurile recent adaugate</h2>
    </template>
    <template #content>
      <DataTable :value="props.vaccines" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="provider" header="Furnizorul" sortable> </Column>
        <Column field="date_received" header="Data primirii" sortable>
          <template #body="slotProps">
            <span> {{ slotProps.data.original_date_received }} </span>
          </template>
        </Column>
      </DataTable>
    </template>
    <template #footer>
      <RouterLink to="/vaccine" class="p-button p-button-text">Vezi toate vaccinurile</RouterLink>
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
 * @file RecentVaccines.vue
 * @description This component displays the recently added vaccines of the user in a table format.
 */

/**
 * @prop {Array} vaccines - The recent vaccines to be displayed in the table.
 * @prop {Object} cardStyles - The styling options for the card component.
 */
const props = defineProps({
  vaccines: Array,
  cardStyles: Object
})
</script>
