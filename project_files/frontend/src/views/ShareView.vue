<template>
  <div>
    <h2 class="text-2xl font-bold">Date pacient</h2>
    {{ shareData?.patient.name }} {{ shareData?.patient.dob }}
    {{ shareData?.expiration_time }}
  </div>

  <Dialog
    v-model:visible="displayPINCheck"
    modal
    header="Verificare PIN"
    @hide="displayPINCheck = false"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">Introdu PIN-ul pentru a verifica link-ul de partajare</h1>
      <InputOtp v-model="pin" :length="6" :invalid="pinValidation.error ? true : false" />
      <Message v-if="pinValidation.error" severity="error" variant="simple" size="small">{{
        pinValidation.error
      }}</Message>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Verifica" @click="checkPin" :loading="loading" class="w-full" />
    </div>
  </Dialog>

  <Dialog
    v-model:visible="displayInvalid"
    modal
    header="Link expirat"
    @hide="goToLanding"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">Link-ul de partajare a expirat</h1>
      <p>Te rugam sa ceri pacientului tau un nou link de partajare.</p>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Inchide" @click="goToLanding" class="w-full" />
    </div>
  </Dialog>
</template>

<script setup>
import api from '@/services/api'
import { ref, computed, onMounted } from 'vue'
import { z } from 'zod'
import { useRoute, useRouter } from 'vue-router'

const displayPINCheck = ref(false)
const displayInvalid = ref(false)
const pin = ref('')
const route = useRoute()
const router = useRouter()
const shareData = ref(null)

const goToLanding = () => {
  router.push({ path: '/' })
}

onMounted(async () => {
  try {
    const response = await api.get(`/share/${route.params.code}`)
    if (response.data.valid) {
      displayPINCheck.value = true
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
    console.log(route.params.code)
    console.log(pin.value)
    const response = await api.post(`/share/${route.params.code}/verify`, { pin: pin.value })
    if (response.data) {
      shareData.value = response.data
      displayPINCheck.value = false
      console.log(response.data)
    } else {
      pinValidation.value.error = 'PIN-ul este invalid'
    }
  } catch (error) {
    console.error('Error checking PIN:', error)
  }
}
</script>
