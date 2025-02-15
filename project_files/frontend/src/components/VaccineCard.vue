<template>
  <Card style="overflow: hidden" class="w-full" :pt="{ body: { class: 'px-4 py-1' } }">
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
          <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-plain" />
          <Button icon="pi pi-ellipsis-h" class="p-button-rounded p-button-text p-button-plain" @click="toggle" aria-haspopup="true" aria-controls="overlay_menu" />
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
import { defineProps } from 'vue'
import { ref } from 'vue'

defineProps({
  name: String,
  provider: String,
  dateReceived: Date,
})

const menu = ref();
const items = ref([
    {
        label: 'Optiuni',
        items: [
            {
                label: 'Editeaza',
                icon: 'pi pi-pencil'
            },
            {
                label: 'Sterge',
                icon: 'pi pi-trash'
            }
        ]
    }
]);

const toggle = (event) => {
    menu.value.toggle(event);
};

</script>

<style scoped></style>
