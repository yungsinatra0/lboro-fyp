<template>
  <div class="h-full w-full px-4">
    <DataTable :value="filteredHistory" :rows="10" removableSort>
      <Column field="name" header="Vizita"></Column>
      <Column field="doctor_name" header="Numele Doctorului"></Column>
      <Column field="place" header="Locatia"></Column>
      <Column field="date" header="Data"></Column>
      <Column field="category" header="Categoria"></Column>
      <Column field="subcategory" header="Subcategoria"></Column>
      <Column field="notes" header="Notite"></Column>
      <Column field="date_consultation" header="Data Consultatiei"></Column>
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
