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
      >Adauga informatia pentru un semn vital nou. Câmpurile marcate cu <span class="text-red-500">*</span> sunt obligatorii.</span
    >
    
    <!-- Show error message if API returns an error -->
    <Message v-if="errorMessage" severity="error" class="mb-4 w-full">
      {{ errorMessage }}
    </Message>
    
    <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
      <div class="flex items-center gap-4 mb-4">
        <label for="vitalDataTypes" class="font-semibold w-24">
          Tipul semnului vital <span class="text-red-500">*</span>
        </label>
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
      <div class="flex items-center gap-4 mb-4" v-if="$form.vitalDataTypes && $form.vitalDataTypes.value.is_compound === false">
        <label for="value" class="font-semibold w-24">
          Valoarea <span class="text-red-500">*</span>
        </label>
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
      <div class="flex items-center gap-4 mb-4" v-if="$form.vitalDataTypes && $form.vitalDataTypes.value.is_compound === true">
        <label for="valueSystolic" class="font-semibold w-24">
          Valoarea sistolica <span class="text-red-500">*</span>
        </label>
        <InputNumber
          name="valueSystolic"
          class="flex w-1/2 md:w-1/3"
          :maxFractionDigits="2"
          :min="0"
          fluid
        />
        <label for="valueDiastolic" class="font-semibold w-24">
          Valoarea diastolica <span class="text-red-500">*</span>
        </label>
        <InputNumber
          name="valueDiastolic"
          class="flex w-1/2 md:w-1/3"
          :maxFractionDigits="2"
          :min="0"
          fluid
        />
        <span v-if="$form.vitalDataTypes && $form.vitalDataTypes.value"> {{ $form.vitalDataTypes.value.unit }} </span>
        <Message
          v-if="$form.valueSystolic?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.valueSystolic.error.message }}</Message
        >
        <Message
          v-if="$form.valueDiastolic?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.valueDiastolic.error.message }}</Message
        >    
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="dateRecorded" class="font-semibold w-24">
          Data inregistrarii <span class="text-red-500">*</span>
        </label>
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
        <Button label="Salveaza" severity="success" autofocus type="submit" :loading="isSubmitting" />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
/**
 * @file AddVital.vue
 * @description Component for adding a new vital sign measurement. Displays a dialog with a form to input vital sign details, 
 * which then sends a request to the backend to add the measurement.
 */
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import { format } from 'date-fns'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {Array} vitalTypes - Array of vital sign types that can be selected.
 */
const props = defineProps({
  displayDialog: Boolean,
  vitalTypes: Array,
})

/**
 * @emit {Function} add - Emits the 'add' event with the new vital sign data.
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)
const errorMessage = ref('')
const isSubmitting = ref(false)

/**
 * Initial values for the form fields
 */
const initialValues = ref({
  value: 0,
  valueSystolic: 0,
  valueDiastolic: 0,
  dateRecorded: null,
  vitalDataTypes: '',
  notes: '',
})

/**
 * Zod resolver for form validation
 * The resolver uses Zod to define the schema for the form fields and their validation rules.
 */
const resolver = zodResolver(
  z.object({
    value: z.number('Valoarea trebuie sa fie un numar.').positive('Valoarea trebuie sa fie pozitiva.').optional(),
    valueSystolic: z.number('Valoarea trebuie sa fie un numar.').positive('Valoarea trebuie sa fie pozitiva.').optional(),
    valueDiastolic: z.number('Valoarea trebuie sa fie un numar.').positive('Valoarea trebuie sa fie pozitiva.').optional(),
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

/**
 * @description Sends a request to the backend to add a new vital sign measurement with the provided details.
 * Different endpoints are called based on whether the vital sign is compound (like blood pressure) or not.
 * @param {Object} values - The details of the vital sign to be added.
 */
const addVitals = async (values) => {
    isSubmitting.value = true
    errorMessage.value = ''
    
    if (values.vitalDataTypes.is_compound) {
      try {
        let formattedDate = format(values.dateRecorded, 'yyyy-MM-dd')

        const response = await api.post('/me/healthdata/bp', {
          name: values.vitalDataTypes.name,
          value_systolic: values.valueSystolic,
          value_diastolic: values.valueDiastolic,
          date_recorded: formattedDate,
          notes: values.notes,
        })
        emit('add', response.data)
        displayAddDialog.value = false
      } catch (error) {
        console.error('Error adding vital sign:', error)
        errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la adăugarea semnului vital. Vă rugăm să încercați din nou.'
      } finally {
        isSubmitting.value = false
      }
    }
    else {
        try {
            let formattedDate = format(values.dateRecorded, 'yyyy-MM-dd')

            const response = await api.post('/me/healthdata', {
            name: values.vitalDataTypes.name,
            value: values.value,
            date_recorded: formattedDate,
            notes: values.notes,
            })
            emit('add', response.data.healthdata)
            displayAddDialog.value = false
        } catch (error) {
            console.error('Error adding vital sign:', error)
            errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la adăugarea semnului vital. Vă rugăm să încercați din nou.'
        } finally {
            isSubmitting.value = false
        }
    }
}

/**
 * @description Handles form submission
 * @param {Object} e - Form submission event with validation status and values
 */
const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.error('Error adding vital sign: ', e.errors)
    return
  }

  addVitals(e.values)
}
</script>
