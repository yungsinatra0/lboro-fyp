<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Analize laborator
      </h1>
    </div>

    <DataTable
      v-model:expandedRows="expandedRows"
      :value="labTests"
      dataKey="id"
      :rows="11"
      paginator
      v-model:filters="filters"
      :globalFilterFields="['name', 'code']"
    >
      <template #header>
        <div class="flex justify-end align-items-center flex-wrap gap-2">
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText size="small" v-model="filters['global'].value" placeholder="Cauta..." />
          </IconField>
        </div>
      </template>
      <Column expander style="width: 5rem"> </Column>
      <Column field="name" header="Nume"></Column>
      <Column field="code" header="Cod"></Column>
      <!-- TODO: Add small graph for trend of lab results values as column -->
      <template #expansion="slotProps">
        <div class="p-4">
          <h5 class="m-0">Rezultate pentru {{ slotProps.data.name }}</h5>
          <DataTable :value="slotProps.data.results" dataKey="id">
            <Column field="value" header="Rezultat"></Column>
            <Column field="unit" header="Unitate"></Column>
            <Column field="reference_range" header="Interval de referinta"></Column>
            <Column field="method" header="Metoda">
            <template #body="slotProps">
              <span v-if="!slotProps.data.method"> - </span>
              <span v-else>{{ slotProps.data.method }}</span>
            </template></Column>
            <Column field="date_collection" header="Data recoltarii">
              <template #body="slotProps">
                {{ slotProps.data.original_date_collection }}
              </template>
            </Column>
            <Column class="w-24 !text-end" header="Optiuni">
              <template #body="{ data }">
                <div class="flex flex-row gap-2 justify-end">
                  <Button
                    icon="pi pi-eye"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="() => {
                      displayFileDialog = true
                      historyIdForFile = data.medicalhistory.id
                    }"
                    severity="secondary"
                    v-if="data.medicalhistory.file"
                  >
                  </Button>
                  <!-- <Button
                    icon="pi pi-ellipsis-h"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="(event) => toggle(event, data.id)"
                    severity="secondary"
                  ></Button> -->
                </div>
              </template>
            </Column>
            <!-- <Column field="method" header="Metoda"></Column> -->
          </DataTable>
        </div>
      </template>
    </DataTable>

    <ShowFile
      v-if="displayFileDialog"
      :display-dialog="displayFileDialog"
      @close="displayFileDialog = false"
      :history-id="historyIdForFile"
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import ShowFile from '@/components/medhistory/ShowFile.vue'
import { FilterMatchMode } from '@primevue/core/api'
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { parse } from 'date-fns'

const labTests = ref([])
const expandedRows = ref({})
const displayFileDialog = ref(false)
const historyIdForFile = ref(null)
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})

onMounted(() => {
  fetchLabTests()
})

const fetchLabTests = async () => {
  try {
    const response = await api.get('/me/labtests')
    labTests.value = response.data.map((test) => ({
      ...test,
      results: test.results.map((result) => ({
        ...result,
        date_collection: parse(result.date_collection, 'dd-MM-yyyy', new Date()),
        original_date_collection: result.date_collection,
      })),
    }))
  } catch (error) {
    console.error('Error fetching lab tests:', error)
  }
}
</script>
