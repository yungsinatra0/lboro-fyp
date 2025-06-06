<template>
  <Dialog
    v-model:visible="displayEditDialog"
    modal
    class="w-full md:w-3/4 lg:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Actualizează înregistrarea medicală</span>
      </div>
    </template>

    <span class="text-gray-500 dark:text-gray-400 block mb-4 md:mb-8 text-sm md:text-base">
      Actualizează informațiile pentru înregistrarea medicală selectată.
    </span>
    <span class="text-rose-600 text-sm block mb-8">* Câmpurile marcate sunt obligatorii</span>
    
    <Message v-if="formError" severity="error" class="mb-4 w-full">
      {{ formError }}
    </Message>
    
    <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="name" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Descriere <span class="text-rose-600">*</span></label
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
        <label for="doctor_name" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Numele doctorului <span class="text-rose-600">*</span></label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <InputText
            name="doctor_name"
            class="w-full md:w-3/4"
            autocomplete="off"
            type="text"
            fluid
          />
          <Message
            v-if="$form.doctor_name?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.doctor_name.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="place" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Locație</label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <InputText name="place" class="w-full md:w-3/4" autocomplete="off" type="text" fluid />
          <Message
            v-if="$form.place?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.place.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="category" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Categorie <span class="text-rose-600">*</span></label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <Select
            name="category"
            :options="categories"
            placeholder="Selectează categoria"
            class="w-full md:w-3/4"
            fluid
          />
          <Message
            v-if="$form.category?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.category.error.message }}</Message
          >
        </div>
      </div>

      <div
        class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6"
        v-if="$form.category?.value === 'Consultație'"
      >
        <label for="subcategory" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Subcategorie</label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <Select
            name="subcategory"
            :options="subcategories"
            placeholder="Selectează subcategoria"
            class="w-full md:w-3/4"
            fluid
          />
          <Message
            v-if="$form.subcategory?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.subcategory.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6" v-if="$form.category?.value === 'Laborator'">
        <label for="labsubcategory" class="font-semibold text-sm md:text-base w-full md:w-1/4">Subcategorie laborator</label>
        <div class="w-full md:w-3/4 flex flex-col">
          <Select
            name="labsubcategory"
            :options="labsubcategories"
            placeholder="Selectează subcategoria"
            class="w-full md:w-3/4"
            fluid
          />
          <Message
            v-if="$form.labsubcategory?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.labsubcategory.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="date_consultation" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Data efectuării<span class="text-rose-600">*</span></label
        >
        <div class="w-full md:w-3/4 flex flex-col">
          <DatePicker
            name="date_consultation"
            dateFormat="dd/mm/yy"
            placeholder="Data"
            showIcon
            fluid
            class="w-full md:w-3/4"
            :maxDate="maxDate"
          />
          <Message
            v-if="$form.date_consultation?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.date_consultation.error.message }}</Message
          >
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-start gap-2 md:gap-6 mb-6">
        <label for="notes" class="font-semibold text-sm md:text-base w-full md:w-1/4 pt-2"
          >Note</label
        >
        <div class="w-full md:w-3/4 flex flex-col">
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
          :loading="isSubmitting"
        />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
/**
 * @file EditHistory.vue
 * @description Component for editing an existing medical history record. It displays a dialog with a form
 * pre-filled with the current record data and sends a request to update the record in the backend.
 */
import { parse, format } from 'date-fns'
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref, computed } from 'vue'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {Object} medicalHistory - The medical history record to be edited.
 * @prop {Array} categories - List of medical categories to choose from.
 * @prop {Array} subcategories - List of consultation subcategories to choose from.
 * @prop {Array} labsubcategories - List of laboratory subcategories to choose from.
 */
const props = defineProps({
  displayDialog: Boolean,
  medicalHistory: Object,
  categories: Array,
  subcategories: Array,
  labsubcategories: Array,
})

/**
 * @emit {Function} edit - Emits the 'edit' event with the updated medical history data.
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['edit', 'close'])
const maxDate = ref(new Date())
const displayEditDialog = ref(props.displayDialog)
const formError = ref(null)
const isSubmitting = ref(false)

/**
 * @computed {Object} initialValues
 * @description Computes the initial values for the form based on the current medical history record.
 * Handles date parsing and default values for optional fields.
 */
const initialValues = computed(() => {
  if (!props.medicalHistory) return {}

  // Parse date string if in proper format, or use existing Date object
  let consultationDate = props.medicalHistory.date_consultation
  if (typeof consultationDate === 'string') {
    consultationDate = parse(consultationDate, 'dd-MM-yyyy', new Date())
  }

  return {
    name: props.medicalHistory.name,
    doctor_name: props.medicalHistory.doctor_name,
    place: props.medicalHistory.place || '',
    date_consultation: consultationDate,
    category: props.medicalHistory.category,
    subcategory: props.medicalHistory.subcategory,
    labsubcategory: props.medicalHistory.labsubcategory,
    notes: props.medicalHistory.notes || '',
  }
})

/**
 * @constant {Function} resolver
 * @description Form validation resolver using Zod schemas.
 * Validates required fields and ensures the consultation date is not in the future.
 */
const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele înregistrării este obligatoriu.'),
    doctor_name: z.string().nonempty('Numele medicului este obligatoriu.'),
    place: z.string().optional(),
    date_consultation: z
      .date({ message: 'Data consultării este obligatorie.' })
      .nullable()
      .refine((value) => value === null || value <= new Date(), {
        message: 'Data consultării nu poate fi în viitor.',
      }),
    category: z.string().nonempty('Categoria este obligatorie.'),
    subcategory: z.string().optional(),
    labsubcategory: z.string().optional(),
    notes: z.string().optional(),
  }),
)

/**
 * @function updateMedicalHistory
 * @description Sends a PATCH request to the backend to update the medical history record with provided details.
 * Handles errors and loading states during the update process.
 * @param {Object} medicalHistoryDetails - The updated details of the medical history record.
 */
const updateMedicalHistory = async (medicalHistoryDetails) => {
  isSubmitting.value = true
  formError.value = null
  
  try {
    let formattedDate = format(medicalHistoryDetails.date_consultation, 'yyyy-MM-dd')

    if (medicalHistoryDetails.category === 'Imagistică') {
      medicalHistoryDetails.subcategory = null
    } else if (medicalHistoryDetails.category === 'Laborator') {
      medicalHistoryDetails.subcategory = null
    }

    const response = await api.patch(`me/medicalhistory/${props.medicalHistory.id}`, {
      name: medicalHistoryDetails.name,
      doctor_name: medicalHistoryDetails.doctor_name,
      place: medicalHistoryDetails.place || null,
      date_consultation: formattedDate,
      category: medicalHistoryDetails.category,
      subcategory: medicalHistoryDetails.subcategory,
      labsubcategory: medicalHistoryDetails.labsubcategory,
      notes: medicalHistoryDetails.notes || null,
    })

    emit('edit', response.data)
    emit('close')
  } catch (error) {
    console.error('Error updating medical history:', error)
    formError.value = error.response?.data?.detail || 
      'A apărut o eroare la actualizarea înregistrării medicale. Te rugăm să încerci din nou.'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * @function onFormSubmit
 * @description Handles the form submission event.
 * Validates the form data and calls updateMedicalHistory if valid.
 * @param {Object} e - The form submission event.
 */
const onFormSubmit = (e) => {
  if (!e.valid) {
    console.error('Error updating medical history: ', e.errors)
    return
  }

  updateMedicalHistory(e.values)
}
</script>
