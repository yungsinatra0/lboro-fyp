<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza certificatul"
    class="w-full md:w-1/2"
    @hide="emit('close')"
  >
  <!-- TODO: Add option for PDF file  -->
    <Image :src="`http://localhost:8000/files/vaccine/${props.vaccineId}`" alt="Certificat vaccin" preview />

  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import Image from 'primevue/image'
import { ref } from 'vue'

const emit = defineEmits(['close'])

const props = defineProps({
  displayDialog: Boolean,
  vaccineId: String,
})

const visible = ref(props.displayDialog)
</script>
