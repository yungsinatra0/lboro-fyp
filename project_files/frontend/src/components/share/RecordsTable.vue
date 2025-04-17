<template>
  <div>
    <DataTable
      :value="filteredArrangedRecords"
      v-model:expandedRows="expandedRows"
      v-model:selection="selectedParentRows"
      dataKey="type"
      @row-select="onParentRowSelect"
      @row-select-all="onParentRowSelect"
      @row-unselect-all="onParentRowUnselect"
      @row-unselect="onParentRowUnselect"
    >
      <template #header>
        <div class="hidden md:flex justify-end align-items-center flex-wrap gap-2 mb-2">
          <Button
            label="Ultimul an"
            icon="pi pi-calendar"
            class="p-button-outlined mr-2 text-sm"
            @click="
              (() => {
                const now = new Date()
                const oneYearAgo = new Date(now)
                oneYearAgo.setFullYear(now.getFullYear() - 1)
                selectedDates = [oneYearAgo, now]
              })()
            "
          />
          <Button
            label="Ultimele 6 luni"
            icon="pi pi-calendar"
            class="p-button-outlined mr-2 text-sm"
            @click="
              (() => {
                const now = new Date()
                const sixMonthsAgo = new Date(now)
                sixMonthsAgo.setMonth(now.getMonth() - 6)
                selectedDates = [sixMonthsAgo, now]
              })()
            "
          />
          <Button
            label="Ultimele 3 luni"
            icon="pi pi-calendar"
            class="p-button-outlined mr-2 text-sm"
            @click="
              (() => {
                const now = new Date()
                const threeMonthsAgo = new Date(now)
                threeMonthsAgo.setMonth(now.getMonth() - 3)
                selectedDates = [threeMonthsAgo, now]
              })()
            "
          />

          <DatePicker
            v-model="selectedDates"
            placeholder="Selecteaza datele"
            selectionMode="range"
            showIcon
            dateFormat="dd/mm/yy"
            class="text-base"
            showButtonBar
            size="small"
          />
        </div>
      </template>
      <Column selectionMode="multiple" headerStyle="width: 3rem" />
      <Column field="type" header="Tip">
        <template #body="slotProps">
          <span class="font-bold"> {{ slotProps.data.type }} </span>
        </template>
      </Column>
      <Column field="items" header="Numar de elemente">
        <template #body="slotProps">
          <span class="font-bold"> {{ slotProps.data.items.length }} </span>
        </template>
      </Column>
      <Column header="Elemente selectate">
      <template #body="slotProps">
        <span class="font-bold"> {{ selectedChildRowsCount[`${slotProps.data.type}`] }} </span>
      </template>
      </Column>
      <Column expander style="width: 3em" />
      <template #expansion="slotProps">
        <DataTable
          :value="slotProps.data.items"
          v-model:selection="selectedChildRows"
          dataKey="id"
          :rows="10"
          :rowsPerPageOptions="[5, 8, 10]"
          paginator
          paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
          currentPageReportTemplate="{first}-{last} din {totalRecords}"
          @row-select="onChildRowSelect($event, slotProps.data)"
          @row-unselect="onChildRowUnselect($event, slotProps.data)"
          @row-select-all="onChildRowSelect($event, slotProps.data)"
          @row-unselect-all="onChildRowUnselect($event, slotProps.data)"
          v-model:filters="filters"
          :globalFilterFields="['name', 'code', 'allergens']"
        >
          <template #header>
            <div class="flex justify-end align-items-center flex-wrap gap-2 mb-2">
              <IconField>
                <InputIcon>
                  <i class="pi pi-search" />
                </InputIcon>
                <InputText size="small" v-model="filters['global'].value" placeholder="Cauta..." />
              </IconField>
            </div>
          </template>
          <Column selectionMode="multiple" headerStyle="width: 3rem" />
          <template v-for="(value, key) in slotProps.data.items[0]" :key="key">
            <Column :field="key" :header="key" v-if="!excludedColumns.includes(key)" />
          </template>
        </DataTable>
      </template>
      <template #footer>
        <div class="flex justify-between align-items-center flex-wrap gap-2 mb-2">
          <Button
            label="Back"
            severity="secondary"
            icon="pi pi-arrow-left"
            @click="emit('back')"
          />
          <Button
            label="Next"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="emit('next', selectedParentRows, selectedChildRows)"
            :disabled="selectedParentRows.length === 0 && selectedChildRows.length === 0"
          />
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import { FilterMatchMode } from '@primevue/core/api'
import { ref, computed } from 'vue'

const emit = defineEmits(['back', 'next'])

const props = defineProps({
  records: Object,
})

const parentName = (key) => {
  switch (key) {
    case 'vitals':
      return 'Semne vitale'
    case 'medications':
      return 'Medicamente'
    case 'labresults':
      return 'Rezultate laborator'
    case 'vaccines':
      return 'Vaccine'
    case 'allergies':
      return 'Alergii'
    case 'medhistory':
      return 'Istoric medical'
  }
}

const expandedRows = ref({})
const selectedParentRows = ref([])
const selectedChildRows = ref([])
const excludedColumns = [
  'id',
  'date_added',
  'medicalhistory',
  'date_consultation',
  'date_received',
  'date_prescribed',
  'date_recorded',
  'date_collection',
  'date_diagnosed',
]
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})
const selectedDates = ref(null)
const arrangedRecords = computed(() => {
  return Object.entries(props.records).map(([type, items]) => {
    return {
      type: parentName(type),
      items: items,
    }
  })
})

const filteredArrangedRecords = computed(() => {
  if (!selectedDates.value) {
    return arrangedRecords.value
  }

  return arrangedRecords.value
    .map((record) => {
      const startDate = selectedDates.value[0]
      const endDate = selectedDates.value[1]

      // Different date field based on record type
      const getDateField = (item, type) => {
        switch (type) {
          case 'Semne vitale':
            return item.date_recorded
          case 'Medicamente':
            return item.date_prescribed
          case 'Rezultate laborator':
            return item.date_collection
          case 'Vaccine':
            return item.date_received
          case 'Alergii':
            return item.date_diagnosed
          case 'Istoric medical':
            return item.date_consultation
          default:
            return item.date_added
        }
      }

      // Filter items based on date range
      const filteredItems = record.items.filter((item) => {
        const itemDate = getDateField(item, record.type)

        if (!itemDate) return false

        if (startDate && !endDate) {
          return itemDate >= startDate
        } else if (startDate && endDate) {
          return itemDate >= startDate && itemDate <= endDate
        }
        return true
      })

      return {
        ...record,
        items: filteredItems,
      }
    })
    .filter((record) => record.items.length > 0)
})

const onParentRowSelect = (event) => {
  // Check if the event.data is an array or an object
  // If it's an array, all rows are selected so iterate over it and push the items to selectedChildRows
  if (typeof event.data[Symbol.iterator] === 'function') {
    selectedChildRows.value = []
    selectedParentRows.value = []
    for (const row of event.data) {
      selectedParentRows.value = [...selectedParentRows.value, row]
      selectedChildRows.value = [...selectedChildRows.value, ...row.items]
    }
  } else {
    // If it's an object, just push the items to selectedChildRows
    // This is the case when a parent row is selected and it has child rows
    for (const row of event.data.items) {
      if (row) {
        selectedChildRows.value = [...selectedChildRows.value, row]
      }
    }
  }

  console.log('Selected Parent Rows:', selectedParentRows.value)
  console.log('Selected Child Rows:', selectedChildRows.value)
}

const onParentRowUnselect = (event) => {
  if (!event.data) {
    selectedChildRows.value = []
    selectedParentRows.value = []
  } else {
    selectedChildRows.value = selectedChildRows.value.filter((childRow) => {
      return !event.data.items.some((parentRow) => parentRow.id === childRow.id)
    })
  }

  console.log('Selected Parent Rows:', selectedParentRows.value)
  console.log('Selected Child Rows:', selectedChildRows.value)
}

const onChildRowSelect = (event, rowData) => {
  // Check if the event.data is an array or an object
  // If it's an array, all rows are selected so iterate over it and push the items to selectedChildRows
  // If all child rows are selected, need to select the parent row as well
  if (typeof event.data[Symbol.iterator] === 'function') {
    selectedChildRows.value = []
    for (const row of event.data) {
      selectedChildRows.value = [...selectedChildRows.value, row]
    }
    // Add the parent row
    selectedParentRows.value = [...selectedParentRows.value, rowData]
  } else {
    // Check if all child rows are selected and if so, add the parent row to selectedParentRows
    const allChildRows = rowData.items.map((item) => item.id)
    const selectedChildRowsIds = selectedChildRows.value.map((item) => item.id)
    const allSelected = allChildRows.every((id) => selectedChildRowsIds.includes(id))
    if (allSelected) {
      selectedParentRows.value = [...selectedParentRows.value, rowData]
    }
  }

  console.log('Selected Parent Rows:', selectedParentRows.value)
  console.log('Selected Child Rows:', selectedChildRows.value)
}

const onChildRowUnselect = (event, rowData) => {
  if (!event.data) {
    selectedChildRows.value = []
    selectedParentRows.value = selectedParentRows.value.filter((parentRow) => {
      return parentRow.type !== rowData.type
    })
  } else {
    selectedChildRows.value = selectedChildRows.value.filter((row) => {
      return row.id !== event.data.id
    })

    const allChildRows = rowData.items.map((item) => item.id)
    const selectedChildRowsIds = selectedChildRows.value.map((item) => item.id)
    const allSelected = allChildRows.every((id) => selectedChildRowsIds.includes(id))
    if (!allSelected) {
      selectedParentRows.value = selectedParentRows.value.filter((parentRow) => {
        return parentRow.type !== rowData.type
      })
    }
  }

  console.log('Selected Parent Rows:', selectedParentRows.value)
  console.log('Selected Child Rows:', selectedChildRows.value)
}

const selectedChildRowsCount = computed(() => {
  const counts = {}
  
  // Count selected rows for each parent type
  arrangedRecords.value.forEach(parentRow => {
    const childRows = selectedChildRows.value.filter(childRow => {
      return parentRow.items.some(item => item.id === childRow.id)
    })
    counts[parentRow.type] = childRows.length
  })
  
  return counts
})
</script>
