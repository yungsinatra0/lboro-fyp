<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Vizualizeaza certificatul"
    class="w-full md:w-3/4 md:h-3/4"
    @hide="emit('close')"
  >
    <div v-if="metadata?.file_type == 'application/pdf'">
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
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['close'])
const metadata = ref(null)
const props = defineProps({
  displayDialog: Boolean,
  vaccineId: String,
})
const visible = ref(props.displayDialog)

onMounted(() => {
  if (props.vaccineId) {
    fetchMetadata()
  }
})

const fetchMetadata = async () => {
  try {
    const response = await api.get(`/files/vaccine/${props.vaccineId}/metadata`)
    metadata.value = response.data
  } catch (error) {
    console.error('Error fetching metadata:', error)
  }
}
</script>
