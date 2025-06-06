<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    header="Adauga un vaccin"
    class="w-full md:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">
        <span class="font-bold whitespace-nowrap text-2xl">Vaccin nou</span>
      </div>
    </template>
    <span class="text-surface-500 dark:text-surface-400 block mb-8"
      >Adauga informatia pentru un vaccin nou. Câmpurile marcate cu <span class="text-red-500">*</span> sunt obligatorii.</span
    >
    
    <!-- Show error message if API returns an error -->
    <Message v-if="errorMessage" severity="error" class="mb-4 w-full">
      {{ errorMessage }}
    </Message>
    
    <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
      <div class="flex items-center gap-4 mb-4">
        <label for="name" class="font-semibold w-24">Numele vaccinului <span class="text-red-500">*</span></label>
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
        <label for="provider" class="font-semibold w-24">Numele furnizorului <span class="text-red-500">*</span></label>
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
        <label for="dateReceived" class="font-semibold w-24">Data primirii vaccinului <span class="text-red-500">*</span></label>
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
      <FileUpload
        name="certificate"
        mode="basic"
        @select="onSelect"
        :multiple="false"
        :custom-upload="true"
        :maxFileSize="1000000"
        :choose-label="`Alege certificatul de vaccinare`"
        :upload-label="`Incarca`"
        :cancel-label="`Anuleaza`"
      >
        <template #empty>
          <span>Adauga certificatul de vaccinare.</span>
        </template>
      </FileUpload>
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
 * @file AddVaccine.vue
 * @description Component for adding a new vaccine. Displays a dialog with a form to input vaccine details, which then sends a request to the backend to add the vaccine.
 */
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import { format } from 'date-fns'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 */
const props = defineProps({
  displayDialog: Boolean,
})

/**
 * @emit {Function} add - Emits the 'add' event with the new vaccine data.
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)
const uploadedFile = ref(null)
const errorMessage = ref('')
const isSubmitting = ref(false)

const initialValues = ref({
  name: '',
  provider: '',
  dateReceived: null,
})

// Zod resolver for form validation
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

/**
 * @description Sends a POST request to the backend to add a new vaccine with the provided details.
 * @param vaccineDetails - The details of the vaccine to be added.
 */
const addVaccine = async (vaccineDetails) => {
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    let formattedDate = format(vaccineDetails.dateReceived, 'yyyy-MM-dd')

    const response = await api.post('me/vaccines', {
      name: vaccineDetails.name,
      date_received: formattedDate,
      provider: vaccineDetails.provider,
    })

    let hasCertificate = false

    if (uploadedFile.value) {
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      await api.post(`upload/vaccine/${response.data.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      hasCertificate = true
    }

    emit('add', { ...response.data, certificate: hasCertificate })
    emit('close')
  } catch (error) {
    console.error('Error in vaccine operation:', error)
    errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la adăugarea vaccinului. Vă rugăm să încercați din nou.'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * @description Handles file selection from the FileUpload component
 * @param event - The file selection event
 */
const onSelect = (event) => {
  uploadedFile.value = event.files[0] // doing only for one file for now
  console.log(uploadedFile.value)
}

/**
 * @description Handles form submission
 * @param e - Form submission event with validation status and values
 */
const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.error('Error adding vaccine: ', e.errors)
    return
  }

  addVaccine(e.values)
}
</script>
