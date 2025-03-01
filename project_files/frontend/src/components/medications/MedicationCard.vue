<template>
  <Card class="w-full mb-4 shadow-3" :pt="cardStyles">
    <template #header>
      <div class="h-2 w-full rounded-t-lg bg-primary"></div>
    </template>

    <template #content>
      <div class="flex flex-col h-full px-3 pt-3">
        <div class="grid grid-cols-2 gap-x-4 gap-y-3">
          <div class="col-span-2">
            <span class="text-sm text-surface-600 dark:text-surface-400">Medicament</span>
            <div class="flex gap-2 mt-0.5 justify-between">
              <p class="text-base font-semibold text-surface-900 dark:text-surface-0">{{ name }}</p>
              <div class="flex flex-row gap-1">
                <Tag :value="form" rounded severity="info" class="text-sm"></Tag>
                <Tag :value="route" rounded severity="info" class="text-sm"></Tag>
              </div>
            </div>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Doză</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">{{ dosage }}</p>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Frecvență</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
              {{ frequency }}
              <span v-if="time_of_day" class="text-sm">({{ time_of_day }})</span>
            </p>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Data prescrierii</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
              {{ date_prescribed }}
            </p>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Durata tratamentului</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
              {{ duration_days }} zile
            </p>
          </div>

          <div class="col-span-2">
            <span class="text-sm text-surface-600 dark:text-surface-400">Notițe</span>
            <div class="mt-0.5 max-h-16 overflow-y-auto">
              <p
                v-if="notes && notes.length > 0"
                class="text-base text-surface-900 dark:text-surface-0"
              >
                {{ notes }}
              </p>
              <p v-else class="text-base text-surface-400 dark:text-surface-400">Fără notițe</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end px-3 py-2">
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
  time_of_day: String,
  date_prescribed: String,
  duration_days: Number,
  form: String,
  route: String,
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
