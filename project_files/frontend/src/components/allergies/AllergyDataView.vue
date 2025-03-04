<template>
  <div class="card w-full h-full">
    <DataView
      :value="filteredAllergies"
      :layout="layout"
      :sortOrder="sortOrder"
      :sortField="sortField"
    >
      <template #header>
        <div class="flex flex-col md:flex-row justify-between items-center gap-2">
          <div class="flex flex-col gap-2 md:flex-row items-center md:gap-4">
            <InputText
              v-model="searchQuery"
              placeholder="Caută alergie..."
              class="w-full md:w-auto"
            />
            <Select
              v-model="sortKey"
              :options="sortOptions"
              optionLabel="label"
              placeholder="Sorteaza dupa"
              @change="onSortChange($event)"
            />
            <MultiSelect
              v-model="selectedAllergens"
              :options="props.allergens"
              placeholder="Alergeni"
              class="w-full md:w-40"
              filter
              showClear
            />
            <MultiSelect
              v-model="selectedReactions"
              :options="props.reactions"
              placeholder="Simptome"
              class="w-full md:w-40"
              filter
              showClear
            />
            <MultiSelect
              v-model="selectedSeverities"
              :options="props.severities"
              placeholder="Severitati"
              class="w-full md:w-40"
              filter
              showClear
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
          <div v-for="(allergy, index) in slotProps.items" :key="allergy.id" class="w-full mb-4">
            <div
              class="flex flex-col p-0 w-full border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-800 rounded-lg shadow-3"
              :class="{ 'mt-4': index !== 0 }"
            >
              <!-- Content section -->
              <div class="p-4">
                <div class="grid grid-cols-2 gap-x-4 gap-y-3">
                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Alergie la</span>
                    <div class="grid grid-flow-col grid-rows-2 auto-cols-fr gap-1 mt-0.5">
                      <p
                        class="text-base font-semibold text-surface-900 dark:text-surface-0"
                        v-for="allergen in allergy.allergens"
                        :key="allergen"
                      >
                        {{ allergen }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Severitate</span>
                    <div class="mt-0.5">
                      <Tag
                        :value="allergy.severity"
                        :severity="getSeverityType(allergy.severity)"
                        rounded
                      />
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Data diagnosticării</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ allergy.date_diagnosed }}
                    </p>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Simptome</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <Tag
                        v-for="reaction in allergy.reactions"
                        :key="reaction"
                        :value="reaction"
                        severity="info"
                        rounded
                      />
                    </div>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Notițe</span>
                    <div class="mt-0.5 max-h-16 overflow-y-auto">
                      <p
                        v-if="allergy.notes && allergy.notes.length > 0"
                        class="text-base text-surface-900 dark:text-surface-0"
                      >
                        {{ allergy.notes }}
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
                  @click="(event) => toggle(event, allergy.id)"
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
            v-for="allergy in slotProps.items"
            :key="allergy.id"
            class="col-span-12 sm:col-span-6 lg:col-span-4 xl:col-span-3 p-2"
          >
            <div
              class="flex flex-col h-full border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-800 rounded-lg shadow-3"
            >
              <!-- Content section -->
              <div class="p-4 flex-1">
                <div class="grid grid-cols-2 gap-x-4 gap-y-2">
                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Alergie la</span>
                    <div class="grid grid-flow-col grid-rows-2 auto-cols-fr gap-1 mt-0.5">
                      <p
                        class="text-base font-semibold text-surface-900 dark:text-surface-0"
                        v-for="allergen in allergy.allergens"
                        :key="allergen"
                      >
                        {{ allergen }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400">Severitate</span>
                    <div class="mt-0.5">
                      <Tag
                        :value="allergy.severity"
                        :severity="getSeverityType(allergy.severity)"
                        rounded
                      />
                    </div>
                  </div>

                  <div>
                    <span class="text-sm text-surface-600 dark:text-surface-400"
                      >Data diagnosticării</span
                    >
                    <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
                      {{ allergy.date_diagnosed }}
                    </p>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Simptome</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <Tag
                        v-for="reaction in allergy.reactions"
                        :key="reaction"
                        :value="reaction"
                        severity="info"
                        rounded
                      />
                    </div>
                  </div>

                  <div class="col-span-2">
                    <span class="text-sm text-surface-600 dark:text-surface-400">Notițe</span>
                    <div class="mt-0.5 max-h-16 overflow-y-auto">
                      <p
                        v-if="allergy.notes && allergy.notes.length > 0"
                        class="text-base text-surface-900 dark:text-surface-0"
                      >
                        {{ allergy.notes }}
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
                  @click="(event) => toggle(event, allergy.id)"
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
import MultiSelect from 'primevue/multiselect';

const props = defineProps({
  allergies: Object,
  allergens: Array,
  reactions: Array,
  severities: Array,
})

const emit = defineEmits(['delete', 'openEdit'])

const layout = ref('grid')
const options = ref(['list', 'grid'])
const confirm = useConfirm()
const menu = ref()
const selectedAllergyId = ref(null)
const sortKey = ref()
const sortOrder = ref()
const sortField = ref()
const sortOptions = ref([
  { label: 'Adaugat tarziu', value: '!date_added' },
  { label: 'Adaugat recent', value: 'date_added' },
])
const selectedAllergens = ref([])
const selectedReactions = ref([])
const selectedSeverities = ref([])
const searchQuery = ref('')

const filteredAllergies = computed(() => {
  
  if (selectedAllergens.value.length > 0) {
    return props.allergies.filter((allergy) =>
      allergy.allergens.some((allergen) => selectedAllergens.value.includes(allergen))
    )
  }

  if (selectedReactions.value.length > 0) {
    return props.allergies.filter((allergy) =>
      allergy.reactions.some((reaction) => selectedReactions.value.includes(reaction))
    )
  }

  if (selectedSeverities.value.length > 0) {
    return props.allergies.filter((allergy) =>
      selectedSeverities.value.includes(allergy.severity)
    )
  }  

  return props.allergies.filter((allergy) =>
    allergy.allergens.some((allergen) =>
      allergen.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  )
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
          if (selectedAllergyId.value) {
            emit('openEdit', selectedAllergyId.value)
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedAllergyId.value) {
            confirmDelete(event, selectedAllergyId.value)
          }
        },
      },
    ],
  },
])

const toggle = (event, id) => {
  selectedAllergyId.value = id
  menu.value.toggle(event)
}

const confirmDelete = (event, id) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Ești sigur că vrei să ștergi această alergie?',
    header: 'Confirmare ștergere',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Șterge',
      severity: 'danger',
    },
    accept: async () => {
      try {
        await api.delete(`/me/allergies/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}

const getSeverityType = (severity) => {
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
</script>
