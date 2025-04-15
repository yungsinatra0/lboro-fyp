<template>
  <div class="flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <div>
        <h2>Date pacient</h2>
        <span> {{ shareData?.patient.name }} </span> <span> {{ shareData?.patient.dob }} </span>
      </div>
      <div>
        <h2>Link-ul expira la</h2>
        <span> {{ shareData?.expiration_time }} </span>
      </div>
    </div>

    <div class="card">
      <Tabs v-model:value="activeTab" v-if="shareData && shareData.items">
        <TabList>
          <Tab v-for="key in Object.keys(shareData.items)" :key="key" :value="key">{{ key }}</Tab>
        </TabList>
        <TabPanels>
          <TabPanel v-for="key in Object.keys(shareData.items)" :key="key" :value="key">
            <DataTable
              v-if="key !== 'Analize de laborator'"
              :value="shareData.items[key]"
              :dataKey=key
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
            >
              <Column
                v-for="column in Object.keys(shareData.items[key][0]).filter(
                  (col) => !['id', 'date_added', 'normal_range', 'trend'].includes(col),
                )"
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
                    @click="() => {
                        recordType = key === 'Vaccinuri' ? 'vaccine' : 'medicalhistory',
                        recordId = data['id']
                        displayFile = true
                    }"
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
            >
              <Column expander style="width: 5rem" />
              <Column field="name" header="Nume"> </Column>
              <Column field="code" header="Cod"> </Column>
              <template #expansion="slotProps">
                <div class="p-4">
                  <h2>Detalii pentru {{ slotProps.data.name }}</h2>
                  <DataTable
                    :value="slotProps.data.results"
                    dataKey="id"
                    :paginator="true"
                    :rows="10"
                    :rowsPerPageOptions="[5, 10, 20]"
                  >
                    <Column
                      v-for="column in Object.keys(slotProps.data.results[0]).filter(
                        (col) => !['id', 'medicalhistory', 'is_numeric', 'date_added'].includes(col),
                      )"
                      :key="column"
                      :field="column"
                      :header="column"
                    ></Column>
                    <Column header="file">
                      <template #body="slotProps">
                        <Button
                          v-if="slotProps.data.medicalhistory.file === true"
                          icon="pi pi-eye"
                          variant="text"
                          severity="secondary"
                          @click="
                            () => {
                              recordType = 'medicalhistory'
                              recordId = slotProps.data.medicalhistory.id
                              displayFile = true
                            }
                          "
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
import { ref } from 'vue'
import ShowSharedFile from './ShowSharedFile.vue'

const activeTab = ref('')
const expandedRows = ref({})
const displayFile = ref(false)
const recordType = ref('')
const recordId = ref('')

const props = defineProps({
  shareData: Object,
  pin: String,
})

console.log('shareData', props.shareData)
</script>
