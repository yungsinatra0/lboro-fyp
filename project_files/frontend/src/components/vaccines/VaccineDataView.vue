<template>
  <div class="card">
    <DataView
      :value="filteredVaccines"
      :layout="layout"
      :sortOrder="sortOrder"
      :sortField="sortField"
    >
      <template #header>
        <div class="flex justify-between items-center">
          <div class="flex flex-row items-center gap-4">
            <InputText
              v-model="searchQuery"
              placeholder="Caută vaccin..."
              class="w-full md:w-auto"
            />
            <Select
              v-model="sortKey"
              :options="sortOptions"
              optionLabel="label"
              placeholder="Sorteaza dupa"
              @change="onSortChange($event)"
            />
            <ToggleButton
              v-model="hasCertificateOnly"
              onLabel="Doar cu certificat"
              offLabel="Toate vaccinele"
              onIcon="pi pi-file-check"
              offIcon="pi pi-list-check"
              class="p-button-sm"
            />
          </div>
          <SelectButton v-model="layout" :options="options" :allowEmpty="false">
            <template #option="{ option }">
              <i :class="[option === 'list' ? 'pi pi-bars' : 'pi pi-table']" />
            </template>
          </SelectButton>
        </div>
      </template>

      <template #list="slotProps">
        <div class="flex flex-col">
          <div v-for="(vaccine, index) in slotProps.items" :key="vaccine.id">
            <div
              class="flex flex-col sm:flex-row sm:items-center p-6 gap-4"
              :class="{ 'border-t border-surface-200 dark:border-surface-700': index !== 0 }"
            >
              <div class="flex flex-col md:flex-row justify-between md:items-center flex-1 gap-6">
                <div class="flex flex-row md:flex-col justify-between items-start gap-2">
                  <div>
                    <span class="text-lg font-bold">{{ vaccine.name }}</span>
                    <div class="font-medium text-surface-500 dark:text-surface-400 mt-2">
                      {{ vaccine.provider }}
                    </div>
                    <div class="text-sm text-surface-600 dark:text-surface-300">
                      {{ vaccine.date_received }}
                    </div>
                  </div>
                </div>
                <div class="flex flex-col md:items-end gap-2">
                  <div class="flex flex-row-reverse md:flex-row gap-2">
                    <Button
                      v-if="vaccine.certificate"
                      icon="pi pi-eye"
                      class="p-button-rounded p-button-text p-button-plain"
                      @click="emit('showFile', vaccine.id)"
                    />
                    <Button
                      icon="pi pi-ellipsis-h"
                      class="p-button-rounded p-button-text p-button-plain"
                      @click="(event) => toggle(event, vaccine.id)"
                      aria-haspopup="true"
                      aria-controls="overlay_menu"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #grid="slotProps">
        <div class="grid grid-cols-12 gap-4">
          <div
            v-for="vaccine in slotProps.items"
            :key="vaccine.id"
            class="col-span-12 sm:col-span-6 md:col-span-4 xl:col-span-3 p-2"
          >
            <div
              class="p-4 border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 rounded flex flex-col h-full"
            >
              <div class="pt-2">
                <div class="text-lg font-bold">{{ vaccine.name }}</div>
                <div class="text-md font-medium mt-2">{{ vaccine.provider }}</div>
                <div class="text-sm text-surface-600 dark:text-surface-300 mt-1">
                  {{ vaccine.date_received }}
                </div>

                <div class="flex gap-2 mt-4 justify-end">
                  <Button
                    v-if="vaccine.certificate"
                    icon="pi pi-eye"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="emit('showFile', vaccine.id)"
                  />
                  <Button
                    icon="pi pi-ellipsis-h"
                    class="p-button-rounded p-button-text p-button-plain"
                    @click="(event) => toggle(event, vaccine.id)"
                    aria-haspopup="true"
                    aria-controls="overlay_menu"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </DataView>

    <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />

    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup>
/**
 * @file VaccineDataView.vue
 * @description Component for displaying a list of vaccines in either grid or list view.
 */
import { ref, computed } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'

/**
 * @prop {Object} vaccines - The list of vaccines to display.
 */
const props = defineProps({
  vaccines: Object,
})

/**
 * @emit {Function} delete - Emitted when a vaccine is deleted.
 * @emit {Function} openEdit - Emitted when a vaccine is edited.
 * @emit {Function} showFile - Emitted when a file is shown.
 */
const emit = defineEmits(['delete', 'openEdit', 'showFile'])

const layout = ref('grid')
const options = ref(['list', 'grid'])
const confirm = useConfirm()
const menu = ref()
const selectedVaccineId = ref(null)
const sortKey = ref()
const sortOrder = ref()
const sortField = ref()
const sortOptions = ref([
  { label: 'Adaugat tarziu', value: 'date_added' },
  { label: 'Adaugat recent', value: '!date_added' },
])
const hasCertificateOnly = ref(false)
const searchQuery = ref('')

/**
 * Sort function to handle the sorting of the vaccines. Taken from PrimeVue documentation.
 * @param event - The event object from the sort change.
 */
const onSortChange = (event) => {
  const value = event.value.value
  const sortValue = event.value

  if (value.indexOf('!') === 0) {
    sortOrder.value = -1
    sortField.value = value.substring(1, value.length)
    sortKey.value = sortValue
  } else {
    sortOrder.value = 1
    sortField.value = value
    sortKey.value = sortValue
  }
}

/**
 * @computed filteredVaccines - Computed property to filter the vaccines based on the search query and certificate status.
 * It filters the vaccines based on the name and provider, and also checks if the vaccine has a certificate.
 */
const filteredVaccines = computed(() => {
  let result = props.vaccines

  if (searchQuery.value) {
    result = result.filter(
      (vaccine) =>
        vaccine.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        vaccine.provider.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (hasCertificateOnly.value) {
    result = result.filter((vaccine) => vaccine.certificate)
  }

  return result
})

// Menu items for the context menu
const menuItems = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          if (selectedVaccineId.value) {
            emit('openEdit', selectedVaccineId.value)
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedVaccineId.value) {
            confirmDelete(event, selectedVaccineId.value)
          }
        },
      },
    ],
  },
])

// Function to handle the toggle of the context menu
const toggle = (event, id) => {
  selectedVaccineId.value = id
  menu.value.toggle(event)
}

// Function to handle the confirmation of deletion of a vaccine
const confirmDelete = (event, id) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Esti sigur ca vrei sa stergi acest vaccin?',
    header: 'Confirmare stergere',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Sterge',
      severity: 'danger',
    },
    accept: async () => {
      try {
        await api.delete(`/me/vaccines/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}
</script>
