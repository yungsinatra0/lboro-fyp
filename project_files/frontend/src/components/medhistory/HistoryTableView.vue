<template>
  <div class="h-full w-full px-4">
    <DataTable 
      v-model:filters="filters" 
      :value="history" 
      :rows="10" 
      paginator 
      dataKey="id" 
      filterDisplay="row"
      :loading="loading"
      :globalFilterFields="['name', 'doctor_name', 'place', 'category']"
      removableSort
    >
      <template #header>
        <div class="flex justify-end">
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText size="small" v-model="filters['global'].value" placeholder="Cauta..." />
          </IconField>
        </div>
      </template>
      
      <template #empty> Nu s-au gasit inregistrari medicale. </template>
      <template #loading> Se incarca datele. Va rugam asteptati. </template>
      
      <Column field="date_consultation" header="Data efectuării" sortable>
        <template #body="slotProps">
          {{ slotProps.data.original_date_consultation }}
        </template>
      </Column>
      
      <Column field="name" header="Descriere">
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" type="text" size="small" @input="filterCallback()" placeholder="Cauta dupa descriere" class="w-full" />
        </template>
      </Column>
      
      <Column field="doctor_name" header="Numele Doctorului">
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" type="text" size="small" @input="filterCallback()" placeholder="Cauta dupa doctor" class="w-full" />
        </template>
      </Column>
      
      <Column field="place" header="Locatia">
        <template #body="slotProps">
          {{ slotProps.data.place ? slotProps.data.place : '-' }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" type="text" size="small" @input="filterCallback()" placeholder="Cauta dupa locatie" class="w-full" />
        </template>
      </Column>
      
      <Column field="category" header="Categoria" :showFilterMenu="false">
        <template #body="slotProps">
          <Tag :value="slotProps.data.category" severity="info" rounded />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Select v-model="filterModel.value" @change="filterCallback()" :options="categories" placeholder="Selecteaza" class="w-full" :showClear="true" size="small">
            <template #option="slotProps">
              <Tag :value="slotProps.option" severity="info" rounded />
            </template>
          </Select>
        </template>
      </Column>
      
      <Column header="Subcategoria">
        <template #body="slotProps">
          <Tag v-if="slotProps.data.subcategory" :value="slotProps.data.subcategory" severity="info" rounded />
          <Tag v-else-if="slotProps.data.labsubcategory" :value="slotProps.data.labsubcategory" severity="info" rounded />
        </template>
      </Column>
      
      <Column field="notes" header="Notite">
        <template #body="slotProps">
          {{ slotProps.data.notes ? slotProps.data.notes : '-' }}
        </template>
      </Column>
      
      <Column class="w-24 !text-end" header="Optiuni">
        <template #body="{ data }">
          <div class="flex flex-row gap-2 justify-end">
            <Button 
              icon="pi pi-eye"
              class="p-button-rounded p-button-text p-button-plain"
              @click="(event) => emit('showFile', data.id)"
              severity="secondary"
              v-if="data.file"
            >
            </Button>
            <Button
              icon="pi pi-ellipsis-h"
              class="p-button-rounded p-button-text p-button-plain"
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
import { ref } from 'vue';
import { FilterMatchMode } from '@primevue/core/api';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import Tag from 'primevue/tag';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Select from 'primevue/dropdown';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';
import api from '@/services/api';

// eslint-disable-next-line no-unused-vars
const props = defineProps({
  history: Array,
  categories: Array,
});

const selectedHistoryId = ref(null);
const menu = ref(null);
const confirm = useConfirm();
const emit = defineEmits(['delete', 'openEdit', 'showFile']);
const loading = ref(false);

// Initialize filters
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  doctor_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  place: { value: null, matchMode: FilterMatchMode.CONTAINS },
  category: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const toggle = (event, id) => {
  selectedHistoryId.value = id;
  menu.value.toggle(event);
};

const menuItems = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          if (selectedHistoryId.value) {
            emit('openEdit', selectedHistoryId.value);
          }
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          if (selectedHistoryId.value) {
            confirmDelete(event, selectedHistoryId.value);
          }
        },
      },
    ],
  },
]);

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
        await api.delete(`/me/medicalhistory/${id}`);
        emit('delete', id);
      } catch (error) {
        console.error(error);
      }
    },
    reject: () => {},
  });
};
</script>