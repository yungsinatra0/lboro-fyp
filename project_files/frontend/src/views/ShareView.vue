<template>
  <SharedItems v-if="isValid && shareData !== null" :share-data="shareData" :pin="pin" />

  <Dialog
    v-if="displayPINCheck"
    v-model:visible="displayPINCheck"
    modal
    header="Verificare PIN"
    @hide="displayPINCheck = false"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">Introdu PIN-ul pentru a verifica link-ul de partajare</h1>
      <span v-if="pinError && pin.length === 6" class="text-red-500 text-sm">{{ pinError }}</span>
      <InputOtp v-model="pin" :length="6" :invalid="pinValidation.error ? true : false" />
      <Message v-if="pinValidation.error" severity="error" variant="simple" size="small">{{
        pinValidation.error
      }}</Message>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Verifica" @click="checkPin" class="w-full" />
    </div>
  </Dialog>

  <Dialog
    v-if="displayInvalid"
    v-model:visible="displayInvalid"
    modal
    header="Link expirat"
    @hide="router.push({ path: '/' })"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">Link-ul de partajare a expirat</h1>
      <p>Te rugam sa ceri pacientului tau un nou link de partajare.</p>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Inchide" @click="router.push({ path: '/' })" class="w-full" />
    </div>
  </Dialog>
</template>

<script setup>
import api from '@/services/api'
import { ref, computed, onMounted, watch } from 'vue'
import { z } from 'zod'
import { useRoute, useRouter } from 'vue-router'
import { parseDates } from '@/utils'
import SharedItems from '@/components/share/SharedItems.vue'

const displayPINCheck = ref(false)
const displayInvalid = ref(false)
const pin = ref('')
const route = useRoute()
const router = useRouter()
const shareData = ref(null)
const isValid = ref(false)
const pinError = ref('')

watch(pin, () => {
  if (pin.value.length < 6) {
    pinError.value = ''
  }
})

onMounted(async () => {
  try {
    const response = await api.get(`/share/${route.params.code}`)
    if (response.data.valid) {
      displayPINCheck.value = true
      isValid.value = true
    }
  } catch (error) {
    console.error('Error fetching share data:', error)
    displayInvalid.value = true
  }
})

const pinValidation = computed(() => {
  const pinSchema = z.string().length(6, { message: 'PIN-ul trebuie sa contina 6 caractere' })
  const result = pinSchema.safeParse(pin.value)

  return {
    success: result.success,
    error: result.success ? null : result.error.format()._errors[0],
  }
})

const checkPin = async () => {
  if (!pinValidation.value.success) {
    return
  }

  try {
    const response = await api.post(`/share/${route.params.code}/verify`, { pin: pin.value })
    if (response.data) {
      shareData.value = {
        ...response.data,
        items: {
          'Semne vitale': parseDates(response.data.items.vitals, 'date_recorded'),
          Medicamente: parseDates(response.data.items.medications, 'date_prescribed'),
          Vaccinuri: parseDates(response.data.items.vaccines, 'date_received'),
          Alergii: parseDates(response.data.items.allergies, 'date_diagnosed'),
          'Istoric medical': parseDates(response.data.items.medicalhistory, 'date_consultation'),
          'Analize de laborator': response.data.items.labtests.map((test) => {
            return {
              ...test,
              results: parseDates(test.results, 'date_collection'),
            }
          }),
        },
      }
      displayPINCheck.value = false
      console.log(shareData.value)
    }
  } catch (error) {
    pinError.value = 'PIN-ul introdus este gresit'
    console.error('Error checking PIN:', error)
  }
}
</script>
