<template>
  <Card :pt="props.cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Istoricul recent adaugat</h2>
    </template>
    <template #content>
      <DataTable :value="props.medhistory" removableSort>
        <Column field="name" header="Numele" sortable> </Column>
        <Column field="doctor_name" header="Doctor" sortable> </Column>
        <Column field="category" header="Categoria">
          <template #body="slotProps">
            <Tag
              :value="slotProps.data.category"
              severity="info"
              rounded
              class="text-sm self-start md:self-auto"
            />
          </template>
        </Column>
        <Column header="Subcategoria">
          <template #body="slotProps">
            <Tag
              v-if="slotProps.data.subcategory"
              :value="slotProps.data.subcategory"
              severity="info"
              rounded
              class="text-sm self-start md:self-auto"
            />
            <Tag
              v-else-if="slotProps.data.labsubcategory"
              :value="slotProps.data.labsubcategory"
              severity="info"
              rounded
              class="text-sm self-start md:self-auto"
            />
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
      <RouterLink to="/istoric" class="p-button p-button-text"
        >Vezi tot istoricul medical
      </RouterLink>
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
 * @file RecentMedicalHistory.vue
 * @description This component displays the recent medical history of the user in a table format.
 */

/**
 * @prop {Array} medhistory - The recent medical history records to be displayed in the table.
 */
const props = defineProps({
  medhistory: Array,
  cardStyles: Object
})


</script>
