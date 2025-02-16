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
        @click="showDialog()"
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
        :id="vaccine.id"
        :name="vaccine.name"
        :provider="vaccine.provider"
        :date-received="vaccine.date_received"
        @delete="deleteVaccine"
        @edit="updateVaccine"
      />
    </div>

    <Dialog v-model:visible="displayDialog" modal header="Adauga un vaccin" class="w-full md:w-1/2">
      <template #header>
        <div class="inline-flex items-center justify-center gap-2">
          <span class="font-bold whitespace-nowrap text-2xl">Vaccin nou</span>
        </div>
      </template>
      <span class="text-surface-500 dark:text-surface-400 block mb-8"
        >Adauga informatia pentru un vaccin nou.</span
      >
      <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
        <div class="flex items-center gap-4 mb-4">
          <label for="name" class="font-semibold w-24">Numele vaccinului</label>
          <InputText name="name" class="flex w-1/2" autocomplete="off" type="text" fluid />
          <Message
            v-if="$form.name?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.name.error.message }}</Message
          >
        </div>
        <div class="flex items-center gap-4 mb-4">
          <label for="provider" class="font-semibold w-24">Numele furnizorului</label>
          <InputText name="provider" class="flex w-1/2" autocomplete="off" type="text" fluid />
          <Message
            v-if="$form.provider?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.provider.error.message }}</Message
          >
        </div>
        <div class="flex items-center gap-4 mb-4">
          <label for="dateReceived" class="font-semibold w-24">Data primirii vaccinului</label>
          <DatePicker
            name="dateReceived"
            dateFormat="dd/mm/yy"
            placeholder="Data"
            showIcon
            fluid
            :maxDate="maxDate"
          />
          <Message
            v-if="$form.dateReceived?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.dateReceived.error.message }}</Message
          >
        </div>
        <!-- <div class="flex items-center gap-5 mb-2">
          <label for="file" class="font-semibold w-24">Certificat de vaccinare</label>
          <FileUpload
            name="file"
            mode="basic"
            accept="image/*"
            maxFileSize="1000000"
            chooseLabel="Incarca fisier"
            uploadLabel="Incarca"
            cancelLabel="Anuleaza"
            @upload="onUpload" />
        </div> -->
        <div class="shrink-0 pt-3 px-5 pb-2 flex justify-end gap-2">
          <Button
            label="Anuleaza"
            outlined
            severity="danger"
            @click="displayDialog = false"
            autofocus
            type="button"
          />
          <Button label="Salveaza" severity="success" autofocus type="submit" />
        </div>
      </Form>
    </Dialog>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import VaccineCard from '@/components/VaccineCard.vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { onMounted, ref } from 'vue'
import InputText from 'primevue/inputtext'
import api from '@/services/api'
import { Form } from '@primevue/forms'
import DatePicker from 'primevue/datepicker'
// import FileUpload from 'primevue/fileupload'
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'

const vaccines = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const response = await api.get('me/vaccines')
    vaccines.value = response.data
  } catch (error) {
    error.value = 'O eroare a aparut la incarcarea vaccinurilor: ' + error.message
  }
  finally {
    loading.value = false
  }
})

const displayDialog = ref(false)
const new_vaccine = ref(null)
const maxDate = ref(new Date())

const showDialog = () => {
  displayDialog.value = true
}

const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele vaccinului este obligatoriu.'),
    provider: z.string().nonempty('Numele furnizorului este obligatoriu.'),
    dateReceived: z
      .date({ message: 'Data primirii vaccinului este obligatorie.' })
      .refine((value) => value < new Date(), {
        message: 'Data primirii vaccinului nu poate fi in viitor.',
      }),
  }),
)

const addVaccine = async (vaccineDetails) => {
  try {
  const response = await api.post('me/vaccines', {
    name: vaccineDetails.name,
    date_received: vaccineDetails.dateReceived,
    provider: vaccineDetails.provider,
  })
  vaccines.value.push(response.data.vaccine)
  } catch (error) {
    console.error('Error adding vaccine:', error)
  }
}

const deleteVaccine = (id) => {
  vaccines.value = vaccines.value.filter((vaccine) => vaccine.id !== id)
}

const updateVaccine = async (id) => {
  try {
    const response = await api.get(`me/vaccines/${id}`)
    new_vaccine.value = response.data
    const index = vaccines.value.findIndex((vaccine) => vaccine.id === id)
    if (index !== -1) {
      vaccines.value[index] = new_vaccine.value
    }
  } catch (error) {
    console.error('Error updating vaccine:', error)
  }
}

const initialValues = ref({
  name: '',
  provider: '',
  dateReceived: null,
})

const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (e.valid) {
    addVaccine(e.values)
    e.reset()
    displayDialog.value = false
  } else if (e.errors) {
    console.log(e.errors)
  }
}
</script>
