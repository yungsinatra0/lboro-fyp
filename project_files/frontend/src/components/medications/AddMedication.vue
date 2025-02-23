<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    class="w-full md:w-3/4 lg:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Medicament nou</span>
      </div>
    </template>

    <span class="text-gray-500 dark:text-gray-400 block mb-4 md:mb-8 text-sm md:text-base">
      Adauga informatia pentru un medicament nou.
    </span>

    <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="name" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Numele medicamentului</label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <InputText name="name" class="w-full md:w-3/4" autocomplete="off" type="text" fluid />
          <Message
            v-if="$form.name?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.name.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="dosage" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Dozajul medicamentului</label
        >
        <div class="w-full md:w-3/4">
          <div class="flex flex-row items-center gap-2">
            <InputText name="dosage" class="w-1/2" autocomplete="off" type="text" fluid />
            <Select
              name="dosageUnits"
              :options="dosageUnits"
              placeholder="Unitate"
              fluid
              class="w-1/2 md:w-1/4"
            />
          </div>
          <div class="flex flex-col mt-1">
            <Message
              v-if="$form.dosage?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
              >{{ $form.dosage.error.message }}</Message
            >
            <Message
              v-if="$form.dosageUnits?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
              >{{ $form.dosageUnits.error.message }}</Message
            >
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="frequency" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Frecventa luarii medicamentului</label
        >
        <div class="w-full md:w-3/4">
          <div class="flex flex-row items-center gap-2">
            <InputNumber
              name="frequency"
              class="w-1/2"
              autocomplete="off"
              inputId="integeronly"
              :min="1"
              placeholder="Frecventa"
              fluid
            />
            <Select
              name="frequencyUnits"
              :options="frequency"
              placeholder="Unitate"
              fluid
              class="w-1/2 md:w-1/4"
            />
          </div>
          <div class="flex flex-col mt-1">
            <Message
              v-if="$form.frequency?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
              >{{ $form.frequency.error.message }}</Message
            >
            <Message
              v-if="$form.frequencyUnits?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
              >{{ $form.frequencyUnits.error.message }}</Message
            >
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-6">
        <label for="datePrescribed" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Data prescrierii medicamentului</label
        >
        <div class="w-full md:w-1/4">
          <DatePicker
            name="datePrescribed"
            dateFormat="dd/mm/yy"
            placeholder="Data"
            showIcon
            fluid
            class="w-full"
            :maxDate="maxDate"
          />
          <Message
            v-if="$form.datePrescribed?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.datePrescribed.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="duration" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Durata luarii medicamentului</label
        >
        <div class="w-full md:w-3/4">
          <IftaLabel class="flex items-center gap-2">
            <InputNumber
              name="duration"
              class="w-1/2 md:w-1/3"
              autocomplete="off"
              inputId="integeronly"
              :min="1"
              fluid
            />
            <label for="duration" class="text-sm md:text-base">Zile</label>
          </IftaLabel>
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="form" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Forma luarii medicamentului</label
        >
        <div class="w-full md:w-3/4">
          <Select name="form" :options="forms" placeholder="Forma" fluid class="w-full md:w-1/3" />
          <Message
            v-if="$form.form?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.form.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="notes" class="font-semibold text-sm md:text-base w-full md:w-1/4">Notite</label>
        <div class="w-full md:w-3/4">
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
      </div>

      <div class="flex justify-end gap-2 mt-6 pt-4 border-t border-gray-200">
        <Button
          label="Anuleaza"
          outlined
          severity="danger"
          @click="emit('close')"
          class="px-4 py-2 text-sm md:text-base"
          type="button"
        />
        <Button
          label="Salveaza"
          severity="success"
          class="px-4 py-2 text-sm md:text-base"
          type="submit"
        />
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
import Select from 'primevue/select'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import IftaLabel from 'primevue/iftalabel'

import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'

const props = defineProps({
  displayDialog: Boolean,
  forms: Array,
})

const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)

const dosageUnits = ref(['mg', 'g', 'ml', 'UI'])

const frequency = ref(['pe zi', 'pe saptamana', 'pe luna'])

const initialValues = ref({
  name: '',
  dosage: '',
  dosageUnits: dosageUnits.value[0],
  frequency: '',
  frequencyUnits: frequency.value[0],
  datePrescribed: null,
  duration: '',
  notes: '',
  form: props.forms[0],
})

const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele medicamentului este obligatoriu.'),
    dosage: z.string().nonempty('Doza medicamentului este obligatorie.'),
    frequency: z
      .number('Frecventa luarii medicamentului trebuie sa fie un numar.')
      .int()
      .positive('Frecventa luarii medicamentului trebuie sa fie un numar pozitiv.'),
    datePrescribed: z
      .date({ message: 'Data prescrierii medicamentului este obligatorie.' })
      .refine((value) => value < new Date(), {
        message: 'Data prescrierii medicamentului nu poate fi in viitor.',
      }),
    duration: z
      .number('Durata tratamentului trebuie sa fie un numar.')
      .int()
      .positive('Durata tratamentului trebuie sa fie un numar pozitiv.'),
    notes: z.string().optional(),
    form: z.string().nonempty('Forma medicamentului este obligatorie.'),
    dosageUnits: z.string().nonempty('Unitatea de masura a dozei este obligatorie.'),
    frequencyUnits: z.string().nonempty('Unitatea de masura a frecventei este obligatorie.'),
  }),
)

const addMedication = async (medicationDetails) => {
  try {
    const response = await api.post('me/medications', {
      name: medicationDetails.name,
      dosage: medicationDetails.dosage + medicationDetails.dosageUnits,
      frequency: medicationDetails.frequency + ' ' + medicationDetails.frequencyUnits,
      date_prescribed: medicationDetails.datePrescribed,
      duration_days: medicationDetails.duration,
      notes: medicationDetails.notes,
      form: medicationDetails.form,
    })

    emit('add', response.data.medication)
    emit('close')
  } catch (error) {
    console.error('Error adding medication:', error)
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
    console.error('Error adding medication: ', e.errors)
    return
  }
  
  addMedication(e.values)
}
</script>
