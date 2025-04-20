<template>
  <div class="h-full w-full px-2 md:px-4">
    <DataTable
      v-model:filters="filters"
      :value="history"
      :rows="5"
      :rowsPerPageOptions="[5, 10, 20]"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
      currentPageReportTemplate="{first}-{last} din {totalRecords}"
      dataKey="id"
      filterDisplay="menu"
      :loading="loading"
      :globalFilterFields="['name', 'doctor_name', 'place', 'category']"
      removableSort
      breakpoint="0px"
      scrollable
      class="text-sm md:text-base"
    >
      <template #header>
        <div class="flex justify-end mb-2">
          <div class="w-full md:w-auto">
            <IconField class="w-full">
              <InputIcon>
                <i class="pi pi-search" />
              </InputIcon>
              <InputText
                class="w-full"
                size="small"
                v-model="filters['global'].value"
                placeholder="Cauta..."
              />
            </IconField>
          </div>
        </div>
      </template>

      <template #empty>
        <div class="p-4 text-center">
          <i class="pi pi-search text-2xl md:text-3xl text-gray-300 dark:text-gray-600 mb-2"></i>
          <p>Nu au fost gasite rezultate care sa corespunda criteriilor de cautare.</p>
        </div>
      </template>
      
      <template #loading>
        <ProgressSpinner />
        Se incarca datele. Va rugam asteptati.
      </template>

      <Column field="name" header="Descriere" :showFilterMenu="true">
        <template #body="slotProps">
          <span class="block truncate max-w-[150px] md:max-w-none">{{ slotProps.data.name }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="w-full"
            @input="filterCallback()"
            placeholder="Cauta dupa descriere"
          />
        </template>
      </Column>

      <Column field="doctor_name" header="Numele Doctorului" :showFilterMenu="true">
        <template #body="slotProps">
          <span class="block truncate max-w-[150px] md:max-w-none">{{
            slotProps.data.doctor_name
          }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="w-full"
            @input="filterCallback()"
            placeholder="Cauta dupa doctor"
          />
        </template>
      </Column>

      <Column field="place" header="Locatia" :showFilterMenu="true">
        <template #body="slotProps">
          <span class="block truncate max-w-[120px] md:max-w-none">{{
            slotProps.data.place ? slotProps.data.place : '-'
          }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="w-full"
            @input="filterCallback()"
            placeholder="Cauta dupa locatie"
          />
        </template>
      </Column>

      <Column field="category" header="Categoria">
        <template #body="slotProps">
          <Tag
            :value="slotProps.data.category"
            severity="info"
            rounded
            class="text-xs md:text-sm"
          />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Select
            v-model="filterModel.value"
            @change="filterCallback()"
            :options="categories"
            placeholder="Selecteaza"
            class="w-full"
            :showClear="true"
            size="small"
          >
            <template #option="slotProps">
              <Tag :value="slotProps.option" severity="info" rounded />
            </template>
          </Select>
        </template>
      </Column>

      <Column header="Subcategoria" class="min-w-[100px]">
        <template #body="slotProps">
          <Tag
            v-if="slotProps.data.subcategory"
            :value="slotProps.data.subcategory"
            severity="info"
            rounded
            class="text-xs md:text-sm"
          />
          <Tag
            v-else-if="slotProps.data.labsubcategory"
            :value="slotProps.data.labsubcategory"
            severity="info"
            rounded
            class="text-xs md:text-sm"
          />
        </template>
      </Column>

      <Column field="notes" header="Notite">
        <template #body="slotProps">
          <span class="text-sm md:text-base">{{
            slotProps.data.notes ? slotProps.data.notes : '-'
          }}</span>
        </template>
      </Column>

      <Column field="date_consultation" header="Data efectuării" sortable>
        <template #body="slotProps">
          <span class="block truncate max-w-full">{{
            slotProps.data.original_date_consultation
          }}</span>
        </template>
      </Column>

      <Column header="Optiuni" style="min-width: 80px">
        <template #body="{ data }">
          <div class="flex flex-row gap-1 md:gap-2 justify-end">
            <Button
              icon="pi pi-eye"
              class="p-button-rounded p-button-text p-button-plain p-1 md:p-2"
              @click="(event) => emit('showFile', data.id)"
              severity="secondary"
              v-if="data.file"
            >
            </Button>
            <Button
              icon="pi pi-ellipsis-h"
              class="p-button-rounded p-button-text p-button-plain p-1 md:p-2"
              @click="(event) => toggle(event, data.id)"
              severity="secondary"
            ></Button>
          </div>
        </template>
      </Column>
    </DataTable>
  </div>
  <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />

  <ConfirmDialog></ConfirmDialog>
</template>

<script setup>
/**
 * @file HistoryTableView.vue
 * @description This file contains the HistoryTableView component, which is used to display the medical history records in a table format using PrimeVue's DataTable component and data fetched from API on the history page.
 */
import { ref } from 'vue'
import { FilterMatchMode } from '@primevue/core/api'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import api from '@/services/api'

/**
 * @prop {Array} history - The medical history records to be displayed in the table.
 * @prop {Array} categories - The list of categories for filtering the history records.
 */
// eslint-disable-next-line no-unused-vars
const props = defineProps({
  history: Array,
  categories: Array,
})

const selectedHistoryId = ref(null)
const menu = ref(null)
const confirm = useConfirm()
/**
 * @emit {Function} delete - Emits the 'delete' event with the ID of the deleted history record.
 * @emit {Function} openEdit - Emits the 'openEdit' event with the ID of the history record to be edited.
 * @emit {Function} showFile - Emits the 'showFile' event with the ID of the history record to show the file.
 */
const emit = defineEmits(['delete', 'openEdit', 'showFile'])
const loading = ref(false)

// Initialize filters used by the DataTable component
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  doctor_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  place: { value: null, matchMode: FilterMatchMode.CONTAINS },
  category: { value: null, matchMode: FilterMatchMode.EQUALS },
})

/**
 * @function toggle - Toggles the visibility of the context menu for editing or deleting a history record.
 * @param event - The event triggered by the button click.
 * @param id - The ID of the history record to be edited or deleted.
 */
const toggle = (event, id) => {
  selectedHistoryId.value = id
  menu.value.toggle(event)
}

/**
 * @constant {Array} menuItems - The items to be displayed in the context menu.
 * Each item has a label, icon, and command to be executed when clicked.
 */
const menuItems = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          if (selectedHistoryId.value) {
            emit('openEdit', selectedHistoryId.value)
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedHistoryId.value) {
            confirmDelete(event, selectedHistoryId.value)
          }
        },
      },
    ],
  },
])

/**
 * @function confirmDelete
 * @description Displays a confirmation dialog before deleting a medical history record. If confirmed, it sends a delete request to the API and emits the 'delete' event with the ID of the record.
 * @param event - The event triggered by the button click.
 * @param id - The ID of the medical history record to be deleted.
 */
const confirmDelete = (event, id) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Esti sigur ca vrei sa stergi aceasta consultatie?',
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
        await api.delete(`/me/medicalhistory/${id}`)
        emit('delete', id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}
</script>
