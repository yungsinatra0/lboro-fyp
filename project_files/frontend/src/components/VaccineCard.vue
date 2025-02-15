<template>
  <Card style="overflow: hidden" class="w-full" :pt="{ body: { class: 'px-4 py-1' } }">
    <template #title>
      <span class="font-bold">{{ name }}</span>
    </template>
    <template #subtitle>
      <div class="flex items-center justify-between">
        <div class="flex flex-col justify-start">
            <span>{{ provider }}</span>
            <span>{{ dateReceived }}</span>
        </div>
        <div>
          <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-plain" />
          <Button icon="pi pi-ellipsis-h" class="p-button-rounded p-button-text p-button-plain" />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Button from 'primevue/button'
import { defineProps } from 'vue'

defineProps({
  name: String,
  provider: String,
  dateReceived: Date,
})
</script>

<style scoped></style>
