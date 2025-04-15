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
              :value="shareData.items[key]"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20]"
            >
              <Column
                v-for="column in Object.keys(shareData.items[key][0])"
                :key="column"
                :field="column"
                :header="column"
                :sortable="true"
              >
                <template #body="{ data }">
                  <span>{{ data[column] }}</span>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('')

const props = defineProps({
  shareData: Object,
})

console.log('shareData', props.shareData) 
</script>
