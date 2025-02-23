<template>
  <NavBar />
  <div class="min-h-screen bg-surface-0 dark:bg-surface-900">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5 text-surface-900 dark:text-surface-0">
        Vaccinele mele
      </h1>
      <Button
        label="Adauga vaccin"
        icon="pi pi-plus"
        class="p-button-outlined mr-2"
        @click="showAddDialog"
      />
    </div>

    <div class="flex flex-col items-center gap-4 p-3 md:p-5">
      <ProgressSpinner v-if="loading" />

      <div v-else-if="error" class="p-4 text-red-500">
        {{ error }}
      </div>

      <div v-else-if="vaccines.length === 0" class="p-4">Nu a fost gasit nici un vaccin.</div>

      <VaccineCard
        v-else
        v-for="vaccine in vaccines"
        :key="vaccine.id"
        v-bind="vaccine"
        :has-certificate="vaccine.certificate ? true : false"
        @delete="deleteVaccine"
        @open-edit="openEditDialog"
        @show-file="showCertificate"
      />
    </div>

    <ConfirmDialog></ConfirmDialog>

    <AddVaccine
      v-if="displayAddDialog"
      @close="displayAddDialog = false"
      @add="addVaccine"
      :display-dialog="displayAddDialog"
    />

    <EditVaccine
      v-if="displayEditDialog"
      @edit="refreshUpdatedVaccine"
      @close="displayEditDialog = false"
      :display-dialog="displayEditDialog"
      :vaccine="editDialogData"
    />

    <ShowCertificate
      v-if="displayCertificateDialog"
      :display-dialog="displayCertificateDialog"
      @close="displayCertificateDialog = false"
      :vaccine-id="vaccineIdForCertificate"
    />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'

import AddVaccine from '@/components/vaccines/AddVaccine.vue'
import VaccineCard from '@/components/vaccines/VaccineCard.vue'
import EditVaccine from '@/components/vaccines/EditVaccine.vue'
import ShowCertificate from '@/components/vaccines/ShowCertificate.vue'

const vaccines = ref([])
const loading = ref(true)
const error = ref(null)

const displayAddDialog = ref(false)
const displayEditDialog = ref(false)
const displayCertificateDialog = ref(false)
const vaccineIdForCertificate = ref(null)
const editDialogData = ref(null)

onMounted(async () => {
  try {
    const response = await api.get('me/vaccines')
    vaccines.value = response.data
  } catch (err) {
    error.value = 'A aparut o eroare la incarcarea vaccinelor' + err
  } finally {
    loading.value = false
  }
})

const showAddDialog = () => {
  displayAddDialog.value = true
}

const addVaccine = (vaccine) => {
  vaccines.value.push(vaccine)
}

const deleteVaccine = (id) => {
  vaccines.value = vaccines.value.filter((vaccine) => vaccine.id !== id)
}

const openEditDialog = (id) => {
  displayEditDialog.value = true
  const vaccine = vaccines.value.find((vaccine) => vaccine.id === id)
  editDialogData.value = vaccine
}

const refreshUpdatedVaccine = (vaccine) => {
  const index = vaccines.value.findIndex((v) => v.id === vaccine.id)
  vaccines.value[index] = vaccine
}

const showCertificate = (id) => {
  displayCertificateDialog.value = true
  vaccineIdForCertificate.value = id
}
</script>
