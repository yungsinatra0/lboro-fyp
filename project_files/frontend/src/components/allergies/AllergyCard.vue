<template>
  <Card class="w-full md:w-1/3 mb-4 shadow-3" :pt="cardStyles">
    <template #header>
      <div class="flex flex-col gap-2">
        <div class="bg-primary h-1 w-full"></div>
        <div class="px-3">
          <h3 class="text-xl font-bold text-surface-900 dark:text-surface-0 mt-1">Alergie</h3>
        </div>
      </div>
    </template>

    <template #content>
      <div class="flex flex-col gap-2 px-3">
        <div>
          <span class="text-sm text-surface-600 dark:text-surface-400">Alergie la</span>
          <p
            class="text-lg font-semibold text-surface-900 dark:text-surface-0 mt-1"
            v-for="allergen in allergens"
            :key="allergen.id"
          >
            {{ allergen }}
          </p>
        </div>

        <div>
          <span class="text-sm text-surface-600 dark:text-surface-400">Severitate</span>
          <div class="mt-1">
            <Tag :value="severity" :severity="getSeverityType(severity)" rounded />
          </div>
        </div>

        <div>
          <span class="text-sm text-surface-600 dark:text-surface-400">Simptome</span>
          <div class="flex flex-wrap gap-1 mt-1">
            <Tag
              v-for="reaction in reactions"
              :key="reaction"
              :value="reaction"
              severity="info"
              rounded
            />
          </div>
        </div>

        <div>
          <span class="text-sm text-surface-600 dark:text-surface-400">Data diagnosticării</span>
          <p class="text-base text-surface-900 dark:text-surface-0 mt-1">{{ date_diagnosed }}</p>
        </div>

        <div class="flex flex-col" v-if="notes">
          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Notițe:</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-1">{{ notes }}</p>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end px-3">
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
import api from '../../services/api'

const emit = defineEmits(['delete', 'openEdit'])

const props = defineProps({
  id: Number,
  reactions: Array,
  allergens: Array,
  severity: String,
  date_diagnosed: String,
  notes: String,
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
        await api.delete(`/me/allergies/${props.id}`)
        emit('delete', props.id)
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
