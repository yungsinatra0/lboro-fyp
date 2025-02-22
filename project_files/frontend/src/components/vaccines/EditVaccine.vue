<template>
  <Dialog
    v-model:visible="displayEditDialog"
    modal
    header="Adauga un vaccin"
    class="w-full md:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">
        <span class="font-bold whitespace-nowrap text-2xl">Actualizeaza vaccinul</span>
      </div>
    </template>
    <span class="text-surface-500 dark:text-surface-400 block mb-8"
      >Actualizeaza informatia pentru vaccinul selectat.</span
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
          @click="emit('close')"
          autofocus
          type="button"
        />
        <Button label="Salveaza" severity="success" autofocus type="submit" />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import { Form } from '@primevue/forms'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import Button from 'primevue/button'
// import FileUpload from 'primevue/fileupload'

import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import { parse } from 'date-fns'

const props = defineProps({
  displayDialog: Boolean,
  vaccine: Object
})
const emit = defineEmits(['edit', 'close'])
const maxDate = ref(new Date())
const displayEditDialog = ref(props.displayDialog)

const initialValues = ref({
  name: props.vaccine.name,
  provider: props.vaccine.provider,
  dateReceived: parse(props.vaccine.date_received, 'dd-MM-yyyy', new Date()),
})

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

const updateVaccine = async (vaccineDetails) => {
  try {
    const response = await api.patch(`me/vaccines/${props.vaccine.id}`, {
      name: vaccineDetails.name,
      date_received: vaccineDetails.dateReceived,
      provider: vaccineDetails.provider,
    })
    emit('edit', response.data.vaccine)
    emit('close')
  } catch (error) {
    console.error('Error updating vaccine:', error)
  }
}

const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.error('Error updating vaccine: ', e.errors)
    return
  }

  updateVaccine(e.values)
}
</script>
