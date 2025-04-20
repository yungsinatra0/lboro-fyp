<template>
  <Card :pt="props.cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Alergiile severe/moderate recent adaugate</h2>
    </template>
    <template #content>
      <DataTable :value="props.allergies" removableSort>
        <Column field="allergen" header="Alergenii" sortable>
          <template #body="slotProps">
            <span v-if="slotProps.data.allergens.length === 1">
              {{ slotProps.data.allergens[0] }}
            </span>
            <span v-else>
              {{
                slotProps.data.allergens[0] +
                ' + ' +
                (slotProps.data.allergens.length - 1) +
                ' alergeni'
              }}
            </span>
          </template>
        </Column>
        <Column field="reactions" header="Reactii" sortable>
          <template #body="slotProps">
            <span v-if="slotProps.data.reactions.length === 1">
              {{ slotProps.data.reactions[0] }}
            </span>
            <span v-else>
              {{
                slotProps.data.reactions[0] +
                ' + ' +
                (slotProps.data.reactions.length - 1) +
                ' reactii'
              }}
            </span>
          </template>
        </Column>
        <Column field="severity" header="Severitate" sortable>
          <template #body="slotProps">
            <Tag
              :value="slotProps.data.severity"
              :severity="getSeverity(slotProps.data.severity)"
            />
          </template>
        </Column>
      </DataTable>
    </template>
    <template #empty>
      <div class="flex flex-col items-center justify-center h-full">
        <i class="pi pi-exclamation-triangle text-4xl text-surface-500 dark:text-surface-400"></i>
        <span class="text-lg text-surface-500 dark:text-surface-400"
          >Nu există date disponibile</span
        >
      </div>
    </template>
    <template #footer>
      <div class="flex justify-center">
        <RouterLink to="/alergii" class="p-button p-button-text">Vezi toate allergiile</RouterLink>
      </div>
    </template>
  </Card>
</template>

<script setup>
/**
 * @file RecentAllergies.vue
 * @description This component displays the recently added severe/moderate allergies of the user.
 */

/**
 * @prop {Array} allergies - The recent allergies to be displayed in the table.
 * @prop {Object} cardStyles - The styling options for the card component.
 */
const props = defineProps({
  allergies: Array,
  cardStyles: Object
})

/**
 * Utility function to get the severity of the allergy and map it to a corresponding color for the tag component.
 * @param severity {string} - The severity of the allergy.
 */
const getSeverity = (severity) => {
  switch (severity) {
    case 'Ușoară':
      return 'success'
    case 'Moderată':
      return 'warn'
    case 'Severă':
      return 'danger'
    default:
      return 'info'
  }
}
</script>
