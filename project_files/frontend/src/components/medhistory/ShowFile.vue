<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza fisierul"
    class="w-full md:w-3/4 md:h-3/4"
    @hide="emit('close')"
  >
    <div class="w-full flex justify-center items-center" v-if="loading">
      <ProgressSpinner />
    </div>
    
    <div v-else-if="error" class="p-4 text-red-500">
      {{ error }}
    </div>
    
    <!-- PDF display -->
    <div v-else-if="metadata?.file_type == 'application/pdf'">
      <object
        :data="`http://localhost:8000/files/medicalhistory/${props.historyId}`"
        type="application/pdf"
        class="w-full h-[70vh] hidden md:block"
      />

      <!-- Download if on mobile -->
      <div class="block md:hidden text-center mt-2">
        <a
          :href="`http://localhost:8000/files/medicalhistory/${props.historyId}`"
          target="_blank"
          class="bg-blue-500 text-white px-4 py-2 rounded-md inline-block mb-4"
        >
          Deschide certificatul PDF
        </a>
      </div>
    </div>

    <!-- Image display -->
    <Image
      v-else
      :src="`http://localhost:8000/files/medicalhistory/${props.historyId}`"
      alt="Fisier consultatie"
      class="w-full h-screen"
      preview
    />
  </Dialog>
</template>

<script setup>
/**
 * @file ShowFile.vue
 * @description Component for displaying a file from the medical history.
 */
import { ref, onMounted } from 'vue'
import api from '@/services/api'

/**
 * @emit close - Emitted when the dialog is closed.
 */
const emit = defineEmits(['close'])
const metadata = ref(null)
const error = ref(null)
const loading = ref(true)

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {String} historyId - The ID of the medical history record that contains the file.
 */
const props = defineProps({
  displayDialog: Boolean,
  historyId: String,
})

const visible = ref(props.displayDialog)

onMounted(() => {
  if (props.historyId) {
    fetchMetadata()
  } else {
    loading.value = false
    error.value = "Nu a fost furnizat un ID valabil pentru fișier."
  }
})

/**
 * @function fetchMetadata
 * @description Fetches the metadata of the file from the API and handles any errors that occur during the request.
 */
const fetchMetadata = async () => {
  
  try {
    const response = await api.get(`/files/medicalhistory/${props.historyId}/metadata`)
    metadata.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Nu s-a putut încărca fișierul. Te rugăm să încerci din nou mai târziu.'
    console.error('Error fetching metadata:', err)
  } finally {
    loading.value = false
  }
}
</script>
