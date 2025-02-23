<template>
  <Card class="w-full mb-4 shadow-3" :pt="cardStyles">
    <template #header>
      <div class="h-2 w-full rounded-t-lg bg-primary"></div>
    </template>

    <template #content>
      <div class="flex flex-col h-full px-3 pt-3">
        <div class="grid grid-cols-2 gap-x-4 gap-y-3">
          <div class="col-span-2">
            <span class="text-sm text-surface-600 dark:text-surface-400">Alergie la</span>
            <div class="grid grid-flow-col grid-rows-2 auto-cols-fr gap-1">
              <p
                class="text-base font-semibold text-surface-900 dark:text-surface-0 mt-0.5"
                v-for="allergen in allergens"
                :key="allergen.id"
              >
                {{ allergen }}
              </p>
            </div>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Severitate</span>
            <div class="mt-0.5">
              <Tag :value="severity" :severity="getSeverityType(severity)" rounded />
            </div>
          </div>

          <div>
            <span class="text-sm text-surface-600 dark:text-surface-400">Data diagnosticării</span>
            <p class="text-base text-surface-900 dark:text-surface-0 mt-0.5">
              {{ date_diagnosed }}
            </p>
          </div>

          <div class="col-span-2">
            <span class="text-sm text-surface-600 dark:text-surface-400">Simptome</span>
            <div class="flex flex-wrap gap-1 mt-0.5">
              <Tag
                v-for="reaction in reactions"
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
              <p v-if="notes" class="text-base text-surface-900 dark:text-surface-0">
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
import api from '../../services/api'

const emit = defineEmits(['delete', 'openEdit'])

const props = defineProps({
  id: String,
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
