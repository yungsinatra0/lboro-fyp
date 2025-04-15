<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza fisierul"
    class="w-full md:w-3/4 md:h-3/4"
    @hide="emit('close')"
  >
    <div v-if="fileObjectURL && metadata?.file_type == 'application/pdf'">
      <object
        :data="fileObjectURL"
        type="application/pdf"
        class="w-full h-[70vh] hidden md:block"
      />
      <div class="block md:hidden text-center mt-2">
        <a
          :href="fileObjectURL"
          target="_blank"
          class="bg-blue-500 text-white px-4 py-2 rounded-md inline-block mb-4"
        >
          Deschide certificatul PDF
        </a>
      </div>
    </div>

    <div v-else-if="fileObjectURL" class="flex justify-center">
      <Image :src="fileObjectURL" alt="Fisier consultatie" class="w-full max-h-[70vh]" preview />
    </div>

    <div v-else-if="error" class="text-red-500 text-center p-4">
      {{ error }}
    </div>
  </Dialog>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['close'])
const metadata = ref(null)
const fileBlob = ref(null)
const fileObjectURL = ref(null)
const error = ref(null)

const props = defineProps({
  displayDialog: Boolean,
  pin: String,
  code: String,
  recordType: String,
  recordId: String,
})

const visible = ref(props.displayDialog)

onMounted(() => {
  fetchMetadata()
  fetchFile()
})

onBeforeUnmount(() => {
  if (fileObjectURL.value) {
    URL.revokeObjectURL(fileObjectURL.value)
  }
})

const fetchMetadata = async () => {
  try {
    const response = await api.get(
      `/share/${props.code}/${props.recordType}/${props.recordId}/metadata`,
      {
        headers: {
          Authorization: `${props.pin}`,
        },
      },
    )
    metadata.value = response.data
  } catch (err) {
    console.error('Error fetching metadata:', err)
    error.value = 'Nu s-au putut încărca metadatele fișierului'
  }
}

const fetchFile = async () => {
  try {
    const response = await api.get(
      `/share/${props.code}/file/${props.recordType}/${props.recordId}`,
      {
        headers: {
          Authorization: `${props.pin}`,
        },
        responseType: 'blob',
      },
    )
    fileBlob.value = response.data
    fileObjectURL.value = URL.createObjectURL(fileBlob.value)
  } catch (err) {
    console.error('Error fetching file:', err)
    error.value = 'Nu s-a putut încărca fișierul'
  }
}
</script>
