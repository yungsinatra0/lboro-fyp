<template>
  <div class="flex flex-col">
    <div class="flex justify-between items-center mb-6 p-4 bg-gray-50 rounded-lg shadow-sm">
      <div class="flex flex-col">
        <h2 class="text-xl font-semibold text-gray-800 mb-2">Date pacient</h2>
        <div class="flex items-center gap-2">
          <i class="pi pi-user text-primary"></i>
          <span class="font-medium">{{ shareData?.patient.name }}</span>
          <span class="text-gray-500 ml-2">| Data nașterii: {{ shareData?.patient.dob }}</span>
        </div>
      </div>
      <div v-if="timer" class="bg-primary bg-opacity-10 py-2 px-4 rounded-full flex items-center">
        <i class="pi pi-clock mr-2 text-primary"></i>
        <span class="font-mono font-medium">
          {{ timer.hours < 10 ? `0${timer.hours}` : timer.hours }}:{{
            timer.minutes < 10 ? `0${timer.minutes}` : timer.minutes
          }}:{{ timer.seconds < 10 ? `0${timer.seconds}` : timer.seconds }}
        </span>
      </div>
    </div>

    <div class="card">
      <Tabs v-model:value="Object.keys(shareData.items)[0]" v-if="shareData && shareData.items">
        <TabList>
          <Tab v-for="key in Object.keys(shareData.items)" :key="key" :value="key">{{ key }}</Tab>
        </TabList>
        <TabPanels>
          <TabPanel v-for="key in Object.keys(shareData.items)" :key="key" :value="key">
            <DataTable
              v-if="key !== 'Analize de laborator'"
              :value="shareData.items[key]"
              :dataKey="key"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
              paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
              currentPageReportTemplate="{first}-{last} din {totalRecords}"
              v-model:filters="filters"
              :globalFilterFields="['name', 'allergens']"
              removableSort
            >
              <template #header>
                <div class="flex justify-end items-center">
                  <IconField>
                    <InputIcon>
                      <i class="pi pi-search" />
                    </InputIcon>
                    <InputText
                      size="small"
                      v-model="filters['global'].value"
                      placeholder="Cauta..."
                    />
                  </IconField>
                </div>
              </template>
              <Column
                v-for="column in getFilteredColumns(key)"
                :key="column"
                :field="column"
                :header="column"
                :sortable="true"
              >
                <template #body="{ data }">
                  <!-- File/Certificate icons -->
                  <Button
                    v-if="['certificate', 'file'].includes(column) && data[column] === true"
                    icon="pi pi-eye"
                    variant="text"
                    severity="secondary"
                    @click="
                      () => {
                        recordType = key === 'Vaccinuri' ? 'vaccine' : 'medicalhistory'
                        recordId = data['id']
                        displayFile = true
                      }
                    "
                    rounded
                  />

                  <!-- Array items as tags -->
                  <template v-else-if="['allergens', 'reactions'].includes(column)">
                    <Tag
                      v-for="(item, index) in data[column]"
                      :key="index"
                      class="mr-1"
                      severity="info"
                      rounded
                      size="small"
                    >
                      {{ item }}
                    </Tag>
                  </template>

                  <!-- Single value as tag -->
                  <Tag
                    v-else-if="
                      ['route', 'form', 'category', 'subcategory', 'labsubcategory'].includes(
                        column,
                      ) && data[column]
                    "
                    class="mr-1"
                    severity="info"
                    rounded
                    size="small"
                  >
                    {{ data[column] }}
                  </Tag>

                  <!-- Severity value as tag -->
                  <Tag
                    v-else-if="['severity'].includes(column) && data[column]"
                    class="mr-1"
                    :severity="data[column] === 'Severă' ? 'danger' : 'warn'"
                    rounded
                    size="small"
                  >
                    {{ data[column] }}
                  </Tag>

                  <span v-else-if="column.includes('date')">
                    {{ data[`original_${column}`] }}
                  </span>

                  <!-- Regular text value -->
                  <span v-else-if="data[column] !== false">{{ data[column] }}</span>
                </template>
              </Column>
            </DataTable>

            <DataTable
              v-else-if="key === 'Analize de laborator'"
              :value="shareData.items[key]"
              v-model:expandedRows="expandedRows"
              dataKey="name"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
              paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
              currentPageReportTemplate="{first}-{last} din {totalRecords}"
              v-model:filters="filters"
              :globalFilterFields="['name', 'code']"
            >
              <template #header>
                <div class="flex justify-end items-center">
                  <IconField>
                    <InputIcon>
                      <i class="pi pi-search" />
                    </InputIcon>
                    <InputText
                      size="small"
                      v-model="filters['global'].value"
                      placeholder="Cauta..."
                    />
                  </IconField>
                </div>
              </template>
              <Column expander style="width: 5rem" />
              <Column field="name" header="Nume"> </Column>
              <Column field="code" header="Cod"> </Column>
              <Column header="Rezultatul recent">
                <template #body="slotProps">
                  <span v-if="slotProps.data.results && slotProps.data.results.length">
                    {{ slotProps.data.results[slotProps.data.results.length - 1].value }}
                    <span class="text-xs text-gray-400 ml-1">{{
                      slotProps.data.results[slotProps.data.results.length - 1].unit
                    }}</span>
                  </span>
                  <span v-else> - </span>
                </template>
              </Column>
              <Column header="Interval de referinta">
                <template #body="slotProps">
                  <span v-if="slotProps.data.results && slotProps.data.results.length">
                    {{ slotProps.data.results[slotProps.data.results.length - 1].reference_range }}
                    <span class="text-xs text-gray-400 ml-1">{{
                      slotProps.data.results[slotProps.data.results.length - 1].unit
                    }}</span>
                  </span>
                  <span v-else> - </span>
                </template></Column
              >
              <Column header="Trend"> </Column>
              <Column header="Evolutia rezultatelor"> </Column>
              <template #expansion="slotProps">
                <div class="p-4">
                  <h2>Detalii pentru {{ slotProps.data.name }}</h2>
                  <DataTable
                    :value="slotProps.data.results"
                    dataKey="id"
                    :paginator="true"
                    :rows="5"
                    :rowsPerPageOptions="[5, 10, 20]"
                  >
                    <Column
                      v-for="column in getFilteredColumnsLabs(slotProps.data.results[0])"
                      :key="column"
                      :field="column"
                      :header="column"
                    >
                      <template #body="slotProps" v-if="column === 'date_collection'">
                        {{ slotProps.data[`original_${column}`] }}
                      </template>
                    </Column>
                    <Column header="file">
                      <template #body="slotProps">
                        <Button
                          v-if="slotProps.data.medicalhistory.file === true"
                          icon="pi pi-eye"
                          variant="text"
                          severity="secondary"
                          @click="showFile('medicalhistory', slotProps.data.medicalhistory.id)"
                          rounded
                        />
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </template>
            </DataTable>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>

    <ShowSharedFile
      v-if="displayFile"
      :display-dialog="displayFile"
      :pin="pin"
      :code="$route.params.code"
      :record-type="recordType"
      :record-id="recordId"
      @close="displayFile = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ShowSharedFile from './ShowSharedFile.vue'
import { FilterMatchMode } from '@primevue/core/api'
import { parseISO } from 'date-fns'
import { useTimer } from 'vue-timer-hook'

const props = defineProps({
  shareData: Object,
  pin: String,
})

const expandedRows = ref({})
const displayFile = ref(false)
const recordType = ref('')
const recordId = ref('')
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})
const timer = ref(null)

onMounted(() => {
  if (props.shareData.expiration_time) {
    const expirationDate = parseISO(props.shareData.expiration_time)
    timer.value = useTimer(expirationDate)
  }
})

const showFile = (type, id) => {
  recordType.value = type
  recordId.value = id
  displayFile.value = true
}

const getFilteredColumns = (key) => {
  if (!props.shareData?.items?.[key]?.[0]) return []
  return Object.keys(props.shareData.items[key][0]).filter(
    (col) =>
      !['id', 'date_added', 'normal_range', 'trend'].includes(col) && !col.includes('original'),
  )
}

const getFilteredColumnsLabs = (result) => {
  if (!result) return []
  return Object.keys(result).filter(
    (col) =>
      !['id', 'medicalhistory', 'is_numeric', 'date_added'].includes(col) &&
      !col.includes('original'),
  )
}
</script>
