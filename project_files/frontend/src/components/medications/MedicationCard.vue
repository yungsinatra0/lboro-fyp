<template>
  <Card class="w-full mb-4 shadow-3" :pt="cardStyles">
    <template #header>
      <div class="bg-primary h-1 w-full"></div>
    </template>

    <template #title>
      <div class="flex flex-col md:flex-row md:justify-between md:items-center py-2 gap-2">
        <span class="font-bold text-xl text-primary">{{ name }}</span>
        <Tag :value="form" rounded severity="success" class="text-sm self-start md:self-auto"></Tag>
      </div>
    </template>

    <template #content>
      <div class="flex flex-col">
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2">
            <i class="pi pi-clock text-primary"></i>
            <span class="font-bold"
              >Frecvență: <span class="font-medium"> {{ frequency }}</span>
            </span>
          </div>

          <div class="flex items-center gap-2">
            <i class="pi pi-box text-primary"></i>
            <span class="font-bold"
              >Doză: <span class="font-medium"> {{ dosage }}</span>
            </span>
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2">
            <i class="pi pi-calendar text-primary"></i>
            <span class="font-bold"
              >Prescris la data: <span class="font-medium">{{ date_prescribed }}</span></span
            >
          </div>

          <div class="flex items-center gap-2">
            <i class="pi pi-hourglass text-primary"></i>
            <span class="font-bold"
              >Durata tratamentului: <span class="font-medium">{{ duration_days }} zile</span></span
            >
          </div>
        </div>

        <div v-if="notes && notes.length > 0" class="flex flex-col gap-1 mt-1">
          <div class="flex items-start gap-2">
            <i class="pi pi-info-circle text-primary mt-1"></i>
            <div>
              <span class="font-bold">Notițe:</span>
              <p class="m-0 mt-1 text-sm">{{ notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end">
        <Button
          icon="pi pi-ellipsis-h"
          class="p-button-rounded p-button-text p-button-plain"
          @click="toggle"
          aria-haspopup="true"
          aria-controls="overlay_menu"
        />
        <Menu ref="menu" id="overlay_menu" :model="items" :popup="true" />
      </div>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import Tag from 'primevue/tag'
import { ref } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'

const emit = defineEmits(['delete', 'openEdit'])

const props = defineProps({
  id: String,
  name: String,
  dosage: String,
  frequency: String,
  date_prescribed: String,
  duration_days: Number,
  form: String,
  notes: String || null,
})

const menu = ref()
const items = ref([
  {
    label: 'Optiuni',
    items: [
      {
        label: 'Editeaza',
        icon: 'pi pi-pencil',
        command: () => {
          emit('openEdit', props.id)
        },
      },
      {
        label: 'Sterge',
        icon: 'pi pi-trash',
        command: (event) => {
          confirm1(event)
        },
      },
    ],
  },
])

const toggle = (event) => {
  menu.value.toggle(event)
}

const cardStyles = {
  body: { class: 'px-4 py-1' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
}

const confirm = useConfirm()

const confirm1 = (event) => {
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
        await api.delete(`/me/medications/${props.id}`)
        emit('delete', props.id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}
</script>
