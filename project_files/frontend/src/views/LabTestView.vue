<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Analize laborator
      </h1>
    </div>

    <DataTable v-model:expandedRows="expandedRows" :value="labTests" dataKey="id">
      <template #header>
        <div class="flex justify-between align-items-center flex-wrap gap-2">
          <h5 class="m-0">Analize laborator</h5>
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
            <Column field="date_collection" header="Data recoltarii"> <template #body="slotProps"> {{ slotProps.data.original_date_collection}} </template></Column>
            <!-- <Column field="method" header="Metoda"></Column> -->
          </DataTable>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { parse } from 'date-fns'

const labTests = ref([])
const expandedRows = ref({})

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
