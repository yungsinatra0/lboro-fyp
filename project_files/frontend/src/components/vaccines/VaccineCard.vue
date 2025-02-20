<template>
  <Card style="overflow: hidden" class="w-full" :pt="cardStyles">
    <template #title>
      <span class="font-bold text-2xl">{{ name }}</span>
    </template>
    <template #subtitle>
      <div class="flex items-center justify-between">
        <div class="flex flex-col justify-start">
          <span class="font-bold">{{ provider }}</span>
          <span>{{ dateReceived }}</span>
        </div>
        <div>
          <Button
            icon="pi pi-eye"
            class="p-button-rounded p-button-text p-button-plain"
            @click="emit('showFile', props.id)"
            v-if = "hasCertificate"
          />
          <Button
            icon="pi pi-ellipsis-h"
            class="p-button-rounded p-button-text p-button-plain"
            @click="toggle"
            aria-haspopup="true"
            aria-controls="overlay_menu"
          />
          <Menu ref="menu" id="overlay_menu" :model="items" :popup="true" />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import { ref } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/services/api'

const emit = defineEmits(['delete', 'openEdit', 'showFile'])

const props = defineProps({
  id: String,
  name: String,
  provider: String,
  dateReceived: String,
  hasCertificate: Boolean,
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
    message: 'Esti sigur ca vrei sa stergi acest vaccin?',
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
        await api.delete(`/me/vaccines/${props.id}`)
        emit('delete', props.id)
      } catch (error) {
        console.error(error)
      }
    },
    reject: () => {},
  })
}
</script>

<style scoped></style>
