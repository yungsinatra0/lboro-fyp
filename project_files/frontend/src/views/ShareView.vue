<template>
  <!-- Component to display the shared items once the user passes the verification -->
  <SharedItems v-if="isValid && shareData !== null" :share-data="shareData" :pin="pin" />

  <!-- Component to check the PIN if the share link is valid -->
  <Dialog
    v-if="displayPINCheck"
    v-model:visible="displayPINCheck"
    modal
    header="Verificare PIN"
    @hide="displayPINCheck = false"
    class="w-full md:w-1/3"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">Introdu PIN-ul pentru a verifica link-ul de partajare</h1>
      <span v-if="pinError && pin.length === 6" class="text-red-500 text-sm">{{ pinError }}</span>
      <InputOtp v-model="pin" :length="6" :invalid="pinValidation.error ? true : false" />
      <Message v-if="pinValidation.error" severity="error" variant="simple" size="small">{{
        pinValidation.error
      }}</Message>

      <Message severity="info" icon="pi pi-info-circle" size="small">
        <span class="text-sm font-bold">
        Atentie! Informatia partajata a fost introdusa si selectata de catre pacient pentru a fi vizualizata de Dvs., iar noi nu ne asumam responsabilitatea pentru exactitatea si caracterul complet al acesteia.
      </span>
      </Message>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Verifica" @click="checkPin" class="w-1/2" :loading="loading" />
    </div>
  </Dialog>

  <!-- Dialog shown if the link has expired. Pushes user to the landing page. -->
  <Dialog
    v-if="displayInvalid"
    v-model:visible="displayInvalid"
    modal
    header="Link invalid"
    @hide="router.push({ path: '/' })"
  >
    <div class="flex flex-col items-center justify-center gap-4">
      <h1 class="font-bold">{{ errorMessage || 'Link-ul de partajare a expirat' }}</h1>
      <p>Te rugam sa ceri pacientului tau un nou link de partajare.</p>
    </div>
    <div class="flex justify-center mt-4">
      <Button label="Inchide" @click="router.push({ path: '/' })" class="w-full" />
    </div>
  </Dialog>
</template>

<script setup>
/**
 * @file ShareView.vue
 * @description This file contains the ShareView component, which is responsible for displaying the shared items and handling the PIN verification process.
 */
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
const loading = ref(false)
const errorMessage = ref('')

// Watch for changes in the pin value and reset the error message if the length is less than 6
watch(pin, () => {
  if (pin.value.length < 6) {
    pinError.value = ''
  }
})

/**
 * @description On component mount, check if the share link is valid. If valid, show the PIN check dialog.
 */
onMounted(async () => {
  try {
    const response = await api.get(`/share/${route.params.code}`)
    if (response.data.valid) {
      displayPINCheck.value = true
      isValid.value = true
    } else {
      errorMessage.value = 'Link-ul de partajare nu este valid'
      displayInvalid.value = true
    }
  } catch (error) {
    console.error('Error fetching share data:', error)
    errorMessage.value =
      error.response?.data?.detail || 'A apărut o eroare la verificarea link-ului'
    displayInvalid.value = true
  }
})

/**
 * @function pinValidation
 * @description Validates the PIN input using Zod schema. The PIN must be exactly 6 characters long.
 */
const pinValidation = computed(() => {
  const pinSchema = z.string().length(6, { message: 'PIN-ul trebuie sa contina 6 caractere' })
  const result = pinSchema.safeParse(pin.value)

  return {
    success: result.success,
    error: result.success ? null : result.error.format()._errors[0],
  }
})

/**
 * @function checkPin
 * @description Checks the entered PIN against the one stored in the database. If valid, fetches the shared data and updates the shareData ref.
 */
const checkPin = async () => {
  if (!pinValidation.value.success) {
    return
  }

  loading.value = true
  pinError.value = ''

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
    }
  } catch (error) {
    if (error.response?.status === 403) {
      pinError.value = 'PIN-ul introdus este greșit'
    } else {
      pinError.value = error.response?.data?.detail || 'A apărut o eroare la verificarea PIN-ului'
    }
  } finally {
    loading.value = false
  }
}
</script>
