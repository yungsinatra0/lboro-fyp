<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Semne vitale recent inregistrate</h2>
    </template>
    <template #content>
      <DataTable :value="props.vitals" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="value" header="Valoarea" sortable>
          <template #body="slotProps">
            <span v-if="slotProps.data.value">
              {{ slotProps.data.value }} {{ slotProps.data.unit }}
            </span>
            <span v-else>
              {{ slotProps.data.value_systolic }}/{{ slotProps.data.value_diastolic }}
              {{ slotProps.data.unit }}
            </span>
          </template>
        </Column>
        <Column field="date_recorded" header="Adaugat" sortable>
          <template #body="slotProps">
            <span> {{ slotProps.data.original_date_recorded }} </span>
          </template>
        </Column>
        <Column field="trend" header="Trend">
          <template #body="slotProps">
            <i v-if="slotProps.data.trend === 'up'" class="pi pi-arrow-up text-red-500"></i>
            <i
              v-else-if="slotProps.data.trend === 'down'"
              class="pi pi-arrow-down text-red-500"
            ></i>
            <i v-else class="pi pi-minus-circle text-gray-500"></i>
          </template>
        </Column>
      </DataTable>
    </template>
    <template #footer>
      <RouterLink to="/vitale" class="p-button p-button-text">Vezi toate semnele vitale</RouterLink>
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
 * @file RecentHealthData.vue
 * @description This component displays the recently recorded vital signs of the user in a table format.
 */

/**
 * @prop {Array} vitals - The recent vital signs to be displayed in the table.
 * @prop {Object} cardStyles - The styling options for the card component.
 */
const props = defineProps({
  vitals: Array,
  cardStyles: Object,
})
</script>
