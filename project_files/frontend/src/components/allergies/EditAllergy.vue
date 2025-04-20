<template>
  <Dialog
    v-model:visible="displayEditDialog"
    modal
    class="w-full md:w-3/4 lg:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Editeaza alergie</span>
      </div>
    </template>

    <span class="text-gray-500 dark:text-gray-400 block mb-4 md:mb-8 text-sm md:text-base">
      Schimba informația pentru alergia selectată. Câmpurile marcate cu <span class="text-red-500">*</span> sunt obligatorii.
    </span>

    <!-- Show error message if API returns an error -->
    <Message v-if="errorMessage" severity="error" class="mb-4 w-full">
      {{ errorMessage }}
    </Message>

    <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="allergens" class="font-semibold text-sm md:text-base w-full md:w-1/4">
          Alergen <span class="text-red-500">*</span>
        </label>
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
        <label for="reactions" class="font-semibold text-sm md:text-base w-full md:w-1/4">
          Simptome <span class="text-red-500">*</span>
        </label>
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
        <label for="severity" class="font-semibold text-sm md:text-base w-full md:w-1/4">
          Severitate <span class="text-red-500">*</span>
        </label>
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
        <label for="dateDiagnosed" class="font-semibold text-sm md:text-base w-full md:w-1/4">
          Data diagnosticării <span class="text-red-500">*</span>
        </label>
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
          :loading="isSubmitting"
          type="submit"
        />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
/**
 * @file EditAllergy.vue
 * @description Component for editing an existing allergy. Displays a dialog with a form pre-filled with allergy details,
 * which then sends a request to the backend to update the allergy.
 */
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import { parse, format } from 'date-fns'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {Object} allergy - The allergy object to be edited.
 * @prop {Array} allergens - List of allergens to choose from.
 * @prop {Array} reactions - List of reactions to choose from.
 * @prop {Array} severities - List of severities to choose from.
 */
const props = defineProps({
  displayDialog: Boolean,
  allergy: Object,
  allergens: Array,
  reactions: Array,
  severities: Array,
})

/**
 * @emit {Function} edit - Emits the 'edit' event with the updated allergy data.
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['edit', 'close'])
const maxDate = ref(new Date())
const displayEditDialog = ref(props.displayDialog)
const errorMessage = ref('')
const isSubmitting = ref(false)

const initialValues = ref({
  dateDiagnosed: parse(props.allergy.date_diagnosed, 'dd-MM-yyyy', new Date()),
  reactions: props.allergy.reactions,
  allergens: props.allergy.allergens,
  severity: props.allergy.severity,
  notes: props.allergy.notes,
})

// Zod resolver for form validation
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

/**
 * @description Sends a PATCH request to the backend to update an existing allergy with the provided details.
 * @param allergyDetails - The updated details of the allergy.
 */
const updateAllergy = async (allergyDetails) => {
  isSubmitting.value = true
  
  try {
    let formattedDate = format(allergyDetails.dateDiagnosed, 'yyyy-MM-dd')

    const response = await api.patch(`/me/allergies/${props.allergy.id}`, {
      date_diagnosed: formattedDate,
      reactions: allergyDetails.reactions,
      allergens: allergyDetails.allergens,
      severity: allergyDetails.severity,
      notes: allergyDetails.notes,
    })
    emit('edit', response.data)
    emit('close')
  } catch (error) {
    console.error('Error updating allergy: ', error)
    // Access the error detail from FastAPI response
    errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la actualizarea alergiei. Vă rugăm să încercați din nou.'
  } finally {
    isSubmitting.value = false
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
    console.error('Error updating allergy: ', e.errors)
    return
  }

  updateAllergy(e.values)
}
</script>
