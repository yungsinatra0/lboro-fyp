<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza fisierul"
    class="w-full md:w-3/4 md:h-3/4"
    @hide="emit('close')"
  >
    <div v-if="loading" class="flex justify-center items-center p-8">
      <ProgressSpinner />
      <span class="ml-3">Se încarcă fișierul...</span>
    </div>

    <div v-else-if="fileObjectURL && metadata?.file_type == 'application/pdf'">
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
/**
 * @file ShowSharedFile.vue
 * @description Component to display a shared medical file. Supports viewing PDF files and images.
 * Uses the share API to fetch the file using the provided PIN and code.
 */
import { ref, onMounted, onBeforeUnmount } from 'vue'
import api from '@/services/api'

/**
 * @emit {Function} close - Emits when the dialog is closed
 */
const emit = defineEmits(['close'])

const metadata = ref(null)
const fileBlob = ref(null)
const fileObjectURL = ref(null)
const error = ref(null)
const loading = ref(true)

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog
 * @prop {String} pin - PIN code for authorization to access the shared file
 * @prop {String} code - Unique code identifying the share link
 * @prop {String} recordType - Type of medical record (e.g., 'medicalhistory')
 * @prop {String} recordId - ID of the specific record
 */
const props = defineProps({
  displayDialog: Boolean,
  pin: String,
  code: String,
  recordType: String,
  recordId: String,
})

const visible = ref(props.displayDialog)

/**
 * On component mount, fetch the file metadata and the file itself
 */
onMounted(() => {
  fetchMetadata()
  fetchFile()
})

/**
 * Before component unmount, clean up any object URLs to prevent memory leaks
 */
onBeforeUnmount(() => {
  if (fileObjectURL.value) {
    URL.revokeObjectURL(fileObjectURL.value)
  }
})

/**
 * @function fetchMetadata
 * @description Fetches the metadata for the file, including its type and name
 */
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
    error.value = err.response?.data?.detail || 'Nu s-au putut încărca metadatele fișierului'
  }
}

/**
 * @function fetchFile
 * @description Fetches the actual file blob and creates an object URL for display
 */
const fetchFile = async () => {
  loading.value = true
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
  } finally {
    loading.value = false
  }
}
</script>
