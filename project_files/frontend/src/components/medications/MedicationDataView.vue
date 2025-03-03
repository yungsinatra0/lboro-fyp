<template>
  <div class="card">
    <DataView
      :value="filteredMedicine"
      :layout="layout"
      :sortOrder="sortOrder"
      :sortField="sortField"
    >
      <template #header>
        <div class="flex justify-between items-center">
          <div class="flex flex-row items-center gap-4">
            <InputText
              v-model="searchQuery"
              placeholder="Caută medicament..."
              class="w-full md:w-auto"
            />
            <Select
              v-model="sortKey"
              :options="sortOptions"
              optionLabel="label"
              placeholder="Sorteaza dupa"
              @change="onSortChange($event)"
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
        <div class="flex flex-col w-full">
          <div
            v-for="(medication, index) in slotProps.items"
            :key="medication.id"
            class="w-full mb-4"
          >
            <div
              class="flex flex-col p-0 w-full border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-800 rounded-lg shadow-3"
              :class="{ 'mt-4': index !== 0 }"
            >
              <!-- Clean header without blue strip -->

              <!-- Content section -->
              <div class="p-4">
                <div class="grid grid-cols-2 gap-x-4 gap-y-3">
                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Medicament</span>
                    <div class="flex gap-2 mt-0.5 justify-between">
                      <p class="text-base font-semibold text-surface-900 dark:text-surface-0">
                        {{ medication.name }}
                      </p>
                      <div class="flex flex-row gap-1">
                        <Tag :value="medication.form" rounded severity="info" class="text-sm"></Tag>
                        <Tag
                          :value="medication.route"
                          rounded
                          severity="info"
                          class="text-sm"
                        ></Tag>
                      </div>
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Doză</span>
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.dosage }}
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Frecvență</span>
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.frequency }}
                      <span v-if="medication.time_of_day" class="text-sm"
                        >({{ medication.time_of_day }})</span
                      >
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Data prescrierii</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.date_prescribed }}
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Durata tratamentului</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.duration_days }} zile
                    </p>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Notițe</span>
                    <div class="mt-0.5 max-h-16 overflow-y-auto">
                      <p
                        v-if="medication.notes && medication.notes.length > 0"
                        class="text-base text-surface-900 dark:text-surface-0"
                      >
                        {{ medication.notes }}
                      </p>
                      <p v-else class="text-base text-surface-400 dark:text-surface-400">
                        Fără notițe
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer section -->
              <div class="flex justify-end px-3 py-2">
                <Button
                  icon="pi pi-ellipsis-h"
                  class="p-button-rounded p-button-text p-button-plain"
                  @click="(event) => toggle(event, medication.id)"
                  aria-haspopup="true"
                  aria-controls="overlay_menu"
                />
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #grid="slotProps">
        <div class="grid grid-cols-12 gap-4">
          <div
            v-for="medication in slotProps.items"
            :key="medication.id"
            class="col-span-12 sm:col-span-6 lg:col-span-4 xl:col-span-3 p-2"
          >
            <div
              class="flex flex-col h-full border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-800 rounded-lg shadow-3"
            >
              <!-- Clean header without blue strip -->

              <!-- Content section -->
              <div class="p-4 flex-1">
                <div class="grid grid-cols-2 gap-x-4 gap-y-2">
                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Medicament</span>
                    <div class="flex gap-2 mt-0.5 justify-between">
                      <p class="text-base font-semibold text-surface-900 dark:text-surface-0">
                        {{ medication.name }}
                      </p>
                      <div class="flex flex-row gap-1">
                        <Tag :value="medication.form" rounded severity="info" class="text-sm"></Tag>
                        <Tag
                          :value="medication.route"
                          rounded
                          severity="info"
                          class="text-sm"
                        ></Tag>
                      </div>
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Doză</span>
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.dosage }}
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Frecvență</span>
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.frequency }}
                      <span v-if="medication.time_of_day" class="text-sm"
                        >({{ medication.time_of_day }})</span
                      >
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Data prescrierii</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.date_prescribed }}
                    </p>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Durata tratamentului</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ medication.duration_days }} zile
                    </p>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Notițe</span>
                    <div class="mt-0.5 max-h-16 overflow-y-auto">
                      <p
                        v-if="medication.notes && medication.notes.length > 0"
                        class="text-base text-surface-900 dark:text-surface-0"
                      >
                        {{ medication.notes }}
                      </p>
                      <p v-else class="text-base text-surface-400 dark:text-surface-400">
                        Fără notițe
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer section -->
              <div class="flex justify-end px-3 py-2 mt-auto">
                <Button
                  icon="pi pi-ellipsis-h"
                  class="p-button-rounded p-button-text p-button-plain"
                  @click="(event) => toggle(event, medication.id)"
                  aria-haspopup="true"
                  aria-controls="overlay_menu"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </DataView>

    <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DataView from 'primevue/dataview'
import Button from 'primevue/button'
import SelectButton from 'primevue/selectbutton'
import Select from 'primevue/select'
import Menu from 'primevue/menu'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'
import InputText from 'primevue/inputtext'

const props = defineProps({
  medications: Object,
})

const emit = defineEmits(['delete', 'openEdit'])

const layout = ref('grid')
const options = ref(['list', 'grid'])
const confirm = useConfirm()
const menu = ref()
const selectedMedicationId = ref(null)
const sortKey = ref()
const sortOrder = ref()
const sortField = ref()
const sortOptions = ref([
  { label: 'Adaugat tarziu', value: '!date_added' },
  { label: 'Adaugat recent', value: 'date_added' },
  { label: 'Nume A-Z', value: 'name' },
  { label: 'Nume Z-A', value: '!name' },
])
const searchQuery = ref('')

const filteredMedicine = computed(() => {
  return props.medications.filter((medication) => {
    return medication.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

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

const menuItems = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          if (selectedMedicationId.value) {
            emit('openEdit', selectedMedicationId.value)
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedMedicationId.value) {
            confirmDelete(event, selectedMedicationId.value)
          }
        },
      },
    ],
  },
])

const toggle = (event, id) => {
  selectedMedicationId.value = id
  menu.value.toggle(event)
}

const confirmDelete = (event, id) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Esti sigur ca vrei sa stergi acest medicament?',
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
        await api.delete(`/me/medications/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}
</script>
