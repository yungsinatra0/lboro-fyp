<template>
  <Card :pt="cardStyles" class="h-full">
    <template #title>
      <h2 class="text-xl font-bold p-4">Alergiile recent adaugate</h2>
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
    <template #footer>
      <div class="flex justify-center">
        <RouterLink to="/alergii" class="p-button p-button-text">Vezi toate allergiile</RouterLink>
      </div>
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
  allergies: Array,
})

const getSeverity = (severity) => {
  switch (severity) {
    case 'Ușoară':
      return 'success'
    case 'Moderată':
      return 'warning'
    case 'Severă':
      return 'danger'
    default:
      return 'info'
  }
}

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
