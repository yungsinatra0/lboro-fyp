<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center p-6">
      <ProgressSpinner style="width: 50px; height: 50px" />
      <span class="ml-3">Se încarcă datele...</span>
    </div>

    <!-- Empty state when no records exist -->
    <Message v-else-if="!arrangedRecords.length" severity="info" class="mb-4">
      <div class="flex flex-column align-items-center p-4">
        <i class="pi pi-inbox text-5xl mb-3 text-gray-400"></i>
        <h3>Nu există înregistrări medicale</h3>
        <p class="text-center">Nu au fost găsite înregistrări pentru a fi afișate sau partajate.</p>
      </div>
    </Message>

    <DataTable
      v-else
      :value="filteredArrangedRecords"
      v-model:expandedRows="expandedRows"
      v-model:selection="selectedParentRows"
      dataKey="type"
      @row-select="onParentRowSelect"
      @row-select-all="onParentRowSelect"
      @row-unselect-all="onParentRowUnselect"
      @row-unselect="onParentRowUnselect"
    >
      <!-- Header part of the table with date filters -->
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
          
          <Button
            v-if="selectedDates"
            label="Resetare date"
            icon="pi pi-times"
            severity="secondary"
            text
            class="mr-2 text-sm"
            @click="selectedDates = null"
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
        
        <!-- Mobile date selection -->
        <div class="flex md:hidden justify-end align-items-center flex-wrap gap-2 mb-2">
          <Menu ref="mobileMenu" :model="dateMenuItems" :popup="true">
            <template #button>
              <Button icon="pi pi-calendar" label="Filtru dată" severity="secondary" @click="mobileMenu.toggle($event)" />
            </template>
          </Menu>
        </div>
      </template>

      <!-- Parent rows -->
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

      <!-- Expansion data table -->
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
          <!-- Keyword filter -->
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

          <!-- Empty state for filtered records -->
          <template #empty>
            <div class="flex flex-column align-items-center p-4">
              <i class="pi pi-filter-slash text-3xl mb-2 text-gray-400"></i>
              <p>Nu s-au găsit înregistrări care să corespundă filtrelor.</p>
            </div>
          </template>

          <!-- Dynamic column generation -->
          <Column selectionMode="multiple" headerStyle="width: 3rem" />
          <template v-for="(value, key) in slotProps.data.items[0]" :key="key">
            <Column :field="key" :header="key" v-if="!excludedColumns.includes(key)" />
          </template>
        </DataTable>
      </template>

      <!-- Empty state for filtered records -->
      <template #empty>
        <div class="flex flex-column align-items-center p-6">
          <i class="pi pi-filter-slash text-4xl mb-3 text-gray-400"></i>
          <h3>Nu s-au găsit rezultate</h3>
          <p v-if="selectedDates" class="text-center">
            Nu există înregistrări în intervalul de date selectat.
            <Button label="Resetare filtre" text @click="selectedDates = null" class="p-button-link" />
          </p>
          <p v-else class="text-center">Nu există înregistrări care să corespundă criteriilor de căutare.</p>
        </div>
      </template>

      <!-- Footer with navigation buttons -->
      <template #footer>
        <div class="flex justify-between align-items-center flex-wrap gap-2 mb-2">
          <Button label="Back" severity="secondary" icon="pi pi-arrow-left" @click="emit('back')" />
          <Button
            label="Next"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="emit('next', selectedChildRows)"
            :disabled="selectedChildRows.length === 0"
          />
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
/**
 * @file RecordsTable.vue
 * @description This component displays a table of all of the user's medical records, allowing the user to filter and select records that will be share with a doctor via the share link. 
 */
import { FilterMatchMode } from '@primevue/core/api'
import { ref, computed, onMounted } from 'vue'

/**
 * @emit {Function} back - Emits the back event to navigate to the previous step.
 * @emit {Function} next - Emits the next event to navigate to the next step with the selected child rows.
 * @emit {Function} retry - Emits the retry event to attempt loading the data again.
 */
const emit = defineEmits(['back', 'next', 'retry'])

/**
 * @prop {Object} records - The medical records to be displayed in the table.
 * @prop {Boolean} loading - Indicates if records are being loaded.
 */
const props = defineProps({
  records: Object,
  loading: Boolean,
})

/**
 * @description This function returns the name of the parent row based on the key.
 * @param {string} key - The key of the parent row.
 * @returns {string} - The name of the parent row.
 */
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
    case 'medicalhistory':
      return 'Istoric medical'
  }
}

// UI state variables
const numberCategories = ref(0)
const allSelected = ref(false)
const expandedRows = ref({})
const selectedParentRows = ref([])
const selectedChildRows = ref([])
const mobileMenu = ref(null)

// Date menu for mobile
const dateMenuItems = [
  {
    label: 'Ultimele 3 luni',
    icon: 'pi pi-calendar',
    command: () => {
      const now = new Date()
      const threeMonthsAgo = new Date(now)
      threeMonthsAgo.setMonth(now.getMonth() - 3)
      selectedDates.value = [threeMonthsAgo, now]
    }
  },
  {
    label: 'Ultimele 6 luni',
    icon: 'pi pi-calendar',
    command: () => {
      const now = new Date()
      const sixMonthsAgo = new Date(now)
      sixMonthsAgo.setMonth(now.getMonth() - 6)
      selectedDates.value = [sixMonthsAgo, now]
    }
  },
  {
    label: 'Ultimul an',
    icon: 'pi pi-calendar',
    command: () => {
      const now = new Date()
      const oneYearAgo = new Date(now)
      oneYearAgo.setFullYear(now.getFullYear() - 1)
      selectedDates.value = [oneYearAgo, now]
    }
  },
  {
    label: 'Custom interval',
    icon: 'pi pi-calendar-plus',
    command: () => {
      // Open a dialog for date range picking on mobile
      // This would require adding a dialog component
    }
  },
  {
    label: 'Resetează',
    icon: 'pi pi-times',
    command: () => {
      selectedDates.value = null
    }
  }
]

// Excluded columns from the table
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
  'is_numeric'
]

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})
const selectedDates = ref(null)

/**
 * Updates the number of categories when component mounts or records change
 */
onMounted(() => {
  updateCategoryCount()
})

/**
 * @description Updates the count of record categories
 */
const updateCategoryCount = () => {
  if (props.records) {
    numberCategories.value = Object.keys(props.records).length
  }
}

/**
 * @description 'Parent' function that arranges the records by type.
 * @returns {Array} - The arranged records.
 */
const arrangedRecords = computed(() => {
  if (!props.records || Object.keys(props.records).length === 0) {
    return []
  }
  
  return Object.entries(props.records).map(([type, items]) => {
    return {
      type: parentName(type),
      items: items,
    }
  })
})

/**
 * @description Computed property that filters the arranged records based on the selected dates.
 * @returns {Array} - The filtered arranged records.
 */
const filteredArrangedRecords = computed(() => {
  if (!selectedDates.value) {
    return arrangedRecords.value
  }

  return arrangedRecords.value
    .map((record) => {
      const startDate = selectedDates.value[0]
      const endDate = selectedDates.value[1]

      // Get different date field based on record type
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

/**
 * @description This function is used to select rows in the table.
 * @param {Object} event - The event object.
 */
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
    allSelected.value = true
  } else {
    // If it's an object, just push the items to selectedChildRows
    // This is the case when a parent row is selected and it has child rows
    for (const row of event.data.items) {
      if (row) {
        selectedChildRows.value = [...selectedChildRows.value, row]
      }

      if (numberCategories.value === selectedParentRows.value.length) {
        allSelected.value = true
      }
    }
  }
}

/**
 * @description This function is used to unselect rows in the table.
 * @param {Object} event - The event object.
 */
const onParentRowUnselect = (event) => {
  if (!event.data) {
    selectedChildRows.value = []
    selectedParentRows.value = []
    allSelected.value = false
  } else {
    allSelected.value = false
    selectedChildRows.value = selectedChildRows.value.filter((childRow) => {
      return !event.data.items.some((parentRow) => parentRow.id === childRow.id)
    })
  }
}

/**
 * @description This function is used to select child rows in the table.
 * @param {Object} event - The event object.
 * @param {Object} rowData - The row data object.
 */
const onChildRowSelect = (event, rowData) => {
  // Save a copy of current selectedChildRows before modifications
  const currentSelectedChildRows = [...selectedChildRows.value]
  
  // Check if the event.data is an array or an object
  if (typeof event.data[Symbol.iterator] === 'function') {
    // Add new child rows to selectedChildRows, avoiding duplicates
    for (const row of event.data) {
      if (!currentSelectedChildRows.some(item => item.id === row.id)) {
        selectedChildRows.value.push(row)
      }
    }
  } else {
    // Add single child row if not already selected
    if (!currentSelectedChildRows.some(item => item.id === event.data.id)) {
      selectedChildRows.value.push(event.data)
    }
  }
  
  // Check if all child rows of this parent are now selected
  const allChildRowIds = rowData.items.map(item => item.id)
  const selectedIds = selectedChildRows.value.map(item => item.id)
  const allChildRowsSelected = allChildRowIds.every(id => selectedIds.includes(id))
  
  // Add parent row to selection if all children are selected
  if (allChildRowsSelected && !selectedParentRows.value.some(item => item.type === rowData.type)) {
    selectedParentRows.value.push(rowData)
  }
}

/**
 * @description This function is used to unselect child rows in the table.
 * @param {Object} event - The event object.
 * @param {Object} rowData - The row data object.
 */
const onChildRowUnselect = (event, rowData) => {
  if (!event.data) {
    // Clear all child rows for this parent
    selectedChildRows.value = selectedChildRows.value.filter(row => 
      !rowData.items.some(item => item.id === row.id)
    )
    
    // Remove parent row from selection
    selectedParentRows.value = selectedParentRows.value.filter(parentRow => {
      return parentRow.type !== rowData.type
    })
  } else {
    // Remove specific child row
    selectedChildRows.value = selectedChildRows.value.filter(row => {
      return row.id !== event.data.id
    })

    // Remove parent from selection as not all children are selected anymore
    selectedParentRows.value = selectedParentRows.value.filter(parentRow => {
      return parentRow.type !== rowData.type
    })
  }
}

/**
 * @description Computed property that counts the number of selected child rows for each parent type.
 * @returns {Object} - The counts of selected child rows for each parent type.
 */
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