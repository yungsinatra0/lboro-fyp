<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    class="w-full md:w-3/4 lg:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Alergie nouă</span>
      </div>
    </template>

    <span class="text-gray-500 dark:text-gray-400 block mb-4 md:mb-8 text-sm md:text-base">
      Adaugă informația pentru o alergie nouă.
    </span>

    <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="allergens" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Alergen</label
        >
        <div class="w-full md:w-3/4">
          <MultiSelect
            name="allergens"
            :options="props.allergens"
            placeholder="Selectează alergenul"
            class="w-full md:w-3/4"
            filter
          />
          <Message
            v-if="$form.allergens?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.allergens.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="reactions" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Simptome</label
        >
        <div class="w-full md:w-3/4">
          <MultiSelect
            name="reactions"
            :options="props.reactions"
            placeholder="Selectează simptomele"
            class="w-full md:w-3/4"
            filter
          />
          <Message
            v-if="$form.reactions?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.reactions.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="severity" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Severitate</label
        >
        <div class="w-full md:w-3/4">
          <Select
            name="severity"
            :options="props.severities"
            placeholder="Selectează severitatea"
            class="w-full md:w-3/4"
          />
          <Message
            v-if="$form.severity?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.severity.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="dateDiagnosed" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Data diagnosticării</label
        >
        <div class="w-full md:w-3/4">
          <DatePicker
            name="dateDiagnosed"
            dateFormat="dd/mm/yy"
            placeholder="Data"
            showIcon
            fluid
            class="w-full md:w-3/4"
            :maxDate="maxDate"
          />
          <Message
            v-if="$form.dateDiagnosed?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.dateDiagnosed.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="notes" class="font-semibold text-sm md:text-base w-full md:w-1/4">Note</label>
        <div class="w-full md:w-3/4">
          <Textarea
            name="notes"
            class="w-full md:w-3/4"
            autocomplete="off"
            type="text"
            fluid
            rows="3"
            placeholder="Adaugă note sau observații"
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
          label="Anulează"
          outlined
          severity="danger"
          @click="emit('close')"
          class="px-4 py-2 text-sm md:text-base"
          type="button"
        />
        <Button
          label="Salvează"
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
import { Form } from '@primevue/forms'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import Button from 'primevue/button'
import MultiSelect from 'primevue/multiselect'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'

const props = defineProps({
  displayDialog: Boolean,
  allergens: Array,
  reactions: Array,
  severities: Array,
})

const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)

const initialValues = ref({
  dateDiagnosed: null,
  reactions: [],
  allergens: [],
  severity: '',
  notes: '',
})

const resolver = zodResolver(
  z.object({
    dateDiagnosed: z
      .date({ message: 'Data diagnosticarii este necesara' })
      .refine((value) => value < new Date(), {
        message: 'Data diagnosticarii nu poate fi in viitor',
      }),
    reactions: z.array(z.string()).nonempty({ message: 'Cel putin o reactie este necesara' }),
    allergens: z.array(z.string()).nonempty({ message: 'Cel putin un alergen este necesar' }),
    severity: z.string().nonempty({ message: 'Severitatea este necesara' }),
    notes: z.string().optional(),
  }),
)

const addAllergy = async (allergyDetails) => {
  try {
    const response = await api.post('/me/allergies', {
      date_diagnosed: allergyDetails.dateDiagnosed,
      reactions: allergyDetails.reactions,
      allergens: allergyDetails.allergens,
      severity: allergyDetails.severity,
      notes: allergyDetails.notes,
    })
    emit('add', response.data.allergy)
    emit('close')
  } catch (error) {
    console.error('Error adding allergy: ', error)
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
    console.error('Error adding allergy: ', e.errors)
    return
  }

  addAllergy(e.values)
}
</script>
