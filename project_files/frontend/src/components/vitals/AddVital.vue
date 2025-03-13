<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    header="Adauga un semn vital nou"
    class="w-full md:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">
        <span class="font-bold whitespace-nowrap text-2xl">Semn vital nou</span>
      </div>
    </template>
    <span class="text-surface-500 dark:text-surface-400 block mb-8"
      >Adauga informatia pentru un semn vital nou.</span
    >
    <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
      <div class="flex items-center gap-4 mb-4">
        <label for="vitalDataTypes" class="font-semibold w-24">Tipul semnului vital</label>
        <Select
          name="vitalDataTypes"
          :options="vitalTypes"
          optionLabel="name"
          class="flex w-1/2 md:w-1/3"
          placeholder="Selecteaza tipul"
          fluid
        />
        <Message
          v-if="$form.vitalDataTypes?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.vitalDataTypes.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="value" class="font-semibold w-24">Valoarea semnului</label>
        <InputNumber
          name="value"
          class="flex w-1/2 md:w-1/3"
          :maxFractionDigits="2"
          :min="0"
          fluid
        />
        <span v-if="$form.vitalDataTypes && $form.vitalDataTypes.value"> {{ $form.vitalDataTypes.value.unit }} </span>
        <Message
          v-if="$form.value?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.value.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="dateRecorded" class="font-semibold w-24"
          >Data inregistrarii semnului vital</label
        >
        <DatePicker
          name="dateRecorded"
          dateFormat="dd/mm/yy"
          placeholder="Data"
          showIcon
          fluid
          :maxDate="maxDate"
        />
        <Message
          v-if="$form.dateRecorded?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.dateRecorded.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="notes" class="font-semibold w-24">Notite</label>
        <Textarea
          name="notes"
          class="w-full md:w-3/4"
          autocomplete="off"
          type="text"
          fluid
          rows="3"
        />
        <Message
          v-if="$form.notes?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-xs md:text-sm mt-1"
          >{{ $form.notes.error.message }}</Message
        >
      </div>
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
import InputNumber from 'primevue/inputnumber'
import { Form } from '@primevue/forms'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import Button from 'primevue/button'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'

const props = defineProps({
  displayDialog: Boolean,
  vitalTypes: Array,
})

const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)

const initialValues = ref({
  value: 0,
  dateRecorded: null,
  vitalDataTypes: '',
  notes: '',
})

const resolver = zodResolver(
  z.object({
    value: z.number('Valoarea trebuie sa fie un numar.').positive('Valoarea trebuie sa fie pozitiva.'),
    dateRecorded: z.date().refine((date) => date <= new Date(), {
      message: 'Data inregistrarii nu poate fi in viitor',
    }),
    vitalDataTypes: z.object({
      id: z.string(),
      name: z.string(),
      unit: z.string(),
      is_compound: z.boolean(),
    }).required('Tipul semnului vital este obligatoriu.'),
    notes: z.string().optional(),
  }),
)

const addVitals = async (values) => {
  // will do some logic here soon
}

const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.error('Error adding medication: ', e.errors)
    return
  }

  addVitals(e.values)
}
</script>
