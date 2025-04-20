<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza certificatul"
    class="w-full md:w-3/4 md:h-3/4"
    @hide="emit('close')"
  >
    <!-- Loading indicator -->
    <div v-if="isLoading" class="flex justify-center items-center h-[50vh]">
      <ProgressSpinner strokeWidth="4" animationDuration=".5s" />
      <span class="ml-2">Se încarcă certificatul...</span>
    </div>
    
    <!-- Error message display -->
    <Message v-else-if="errorMessage" severity="error" class="mb-4 w-full">
      {{ errorMessage }}
    </Message>
    
    <!-- PDF Viewer -->
    <div v-else-if="metadata?.file_type == 'application/pdf'">
      <object
        :data="`http://localhost:8000/files/vaccine/${props.vaccineId}`"
        type="application/pdf"
        class="w-full h-[70vh] hidden md:block"
      />

      <div class="block md:hidden text-center">
        <a
          :href="`http://localhost:8000/files/vaccine/${props.vaccineId}`"
          target="_blank"
          class="bg-blue-500 text-white px-4 py-2 rounded-md inline-block mb-4"
        >
          Deschide certificatul PDF
        </a>
      </div>
    </div>

    <!-- Image Viewer -->
    <Image
      v-else
      :src="`http://localhost:8000/files/vaccine/${props.vaccineId}`"
      alt="Certificat vaccin"
      class="w-full h-screen"
      preview
    />
  </Dialog>
</template>
<script setup>
/**
 * @file ShowCertificate.vue
 * @description Component for displaying a vaccine certificate. The certificate can be either a PDF or an image file.
 * It fetches the file metadata first to determine how to render it appropriately.
 */
import { ref, onMounted } from 'vue'
import api from '@/services/api'

/**
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['close'])

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {String} vaccineId - The ID of the vaccine whose certificate should be displayed.
 */
const props = defineProps({
  displayDialog: Boolean,
  vaccineId: String,
})

const metadata = ref(null)
const visible = ref(props.displayDialog)
const isLoading = ref(false)
const errorMessage = ref('')

/**
 * Fetches metadata for the certificate file when the component is mounted
 */
onMounted(() => {
  if (props.vaccineId) {
    fetchMetadata()
  }
})

/**
 * @description Fetches metadata for the certificate file to determine its type
 * and how it should be displayed.
 */
const fetchMetadata = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const response = await api.get(`/files/vaccine/${props.vaccineId}/metadata`)
    metadata.value = response.data
  } catch (error) {
    console.error('Error fetching metadata:', error)
    errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la încărcarea certificatului. Vă rugăm să încercați din nou.'
  } finally {
    isLoading.value = false
  }
}
</script>
