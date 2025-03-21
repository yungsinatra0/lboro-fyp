<template>
  <div class="h-full w-full px-4">
    <DataTable :value="filteredHistory" :rows="10" removableSort>
      <Column field="date_consultation" header="Data Consultatiei" sortable>
        <template #body="slotProps">
          {{ slotProps.data.original_date_consultation }}
        </template>
      </Column>
      <Column field="name" header="Descriere"></Column>
      <Column field="doctor_name" header="Numele Doctorului" sortable></Column>
      <Column field="place" header="Locatia" sortable>
        <template #body="slotProps">
          {{ slotProps.data.place ? slotProps.data.place : '-' }}
        </template>
      </Column>
      <Column field="category" header="Categoria" sortable>
        <template #body="slotProps">
          <Tag :value="slotProps.data.category" severity="info" rounded />
        </template>
      </Column>
      <Column field="subcategory" header="Subcategoria" sortable>
        <template #body="slotProps">
          <Tag :value="slotProps.data.subcategory" severity="info" rounded />
        </template>
      </Column>
      <Column field="notes" header="Notite">
        <template #body="slotProps">
          {{ slotProps.data.notes ? slotProps.data.notes : '-' }}
        </template>
      </Column>
      <!-- TODO: Add view file icon to the last column -->
      <Column class="w-24 !text-end" header="Optiuni">
        <template #body="{ data }">
          <Button
            icon="pi pi-ellipsis-h"
            @click="(event) => toggle(event, data.id)"
            severity="secondary"
          ></Button>
        </template>
      </Column>
    </DataTable>
  </div>
  <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />

  <ConfirmDialog></ConfirmDialog>
</template>

<script setup>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import api from '@/services/api'
import { ref, computed } from 'vue'

const props = defineProps({
  history: Array,
})

const selectedHistoryId = ref(null)
const menu = ref(null)
const confirm = useConfirm()
const emit = defineEmits(['delete', 'openEdit'])

const filteredHistory = computed(() => {
  return props.history
})

const toggle = (event, id) => {
  selectedHistoryId.value = id
  menu.value.toggle(event)
}

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
