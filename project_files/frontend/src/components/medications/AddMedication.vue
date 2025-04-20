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
      Adauga informatia pentru un medicament nou. Câmpurile marcate cu <span class="text-red-500">*</span> sunt obligatorii.
    </span>

    <!-- Show error message if API returns an error -->
    <Message v-if="errorMessage" severity="error" class="mb-4 w-full">
      {{ errorMessage }}
    </Message>

    <Form v-slot="$form" :initialValues @submit="onFormSubmit" :resolver="resolver">
      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
        <label for="name" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Numele medicamentului <span class="text-red-500">*</span></label
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
          >Dozajul medicamentului <span class="text-red-500">*</span></label
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

      <div class="flex flex-col gap-4 md:gap-6 mb-6">
          <div class="flex flex-row gap-4 items-center">
            <label class="font-semibold text-sm md:text-base"> Tipul frecventei <span class="text-red-500">*</span></label>
            <RadioButtonGroup name="frequencyChoice" class="flex flex-row">

              <div class="flex items-center gap-2 ml-2">
                <RadioButton value="standard" inputId="standard" />
                <label for="standard" class="text-sm md:text-base cursor-pointer">Standard</label>
              </div>

              <div class="flex items-center gap-2 ml-2">
                <RadioButton value="alternativ" inputId="alternativ" />
                <label for="alternativ" class="text-sm md:text-base cursor-pointer"
                  >Alternativ</label
                >
              </div>

              <div class="flex items-center gap-2 ml-2">
                <RadioButton value="asNeeded" inputId="asNeeded" />
                <label for="asNeeded" class="text-sm md:text-base cursor-pointer">La nevoie</label>
              </div>

              <div class="flex items-center gap-2 ml-2">
                <RadioButton value="continuu" inputId="continuu" />
                <label for="continuu" class="text-sm md:text-base cursor-pointer">Continuu</label>
              </div>

            </RadioButtonGroup>
            <Message
              v-if="$form.frequencyChoice?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
              >{{ $form.frequencyChoice.error.message }}</Message
            >
          </div>

        <div
          v-if="
            $form.frequencyChoice?.value === 'standard' ||
            $form.frequencyChoice?.value === 'alternativ'
          "
          class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4"
        >
          <label for="frequency" class="font-semibold text-sm md:text-base w-full md:w-1/4">
            Frecventa luarii medicamentului
          </label>
          <div class="flex flex-row items-center gap-2">
            <InputNumber
              name="frequencyValue"
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
              class="w-1/2"
            />
            <Select
              v-if="$form.frequencyValue?.value === 1 && $form.frequencyUnits?.value === 'pe zi'"
              name="timeOfDay"
              :options="['dimineata', 'pranz', 'seara']"
              placeholder="Momentul zilei"
              fluid
              class="w-1/2"
            />
          </div>
          <div class="flex flex-col mt-1">
            <Message
              v-if="$form.frequency?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
            >
              {{ $form.frequency.error.message }}
            </Message>
            <Message
              v-if="$form.frequencyUnits?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
            >
              {{ $form.frequencyUnits.error.message }}
            </Message>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-6">
        <label for="datePrescribed" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Data prescrierii medicamentului <span class="text-red-500">*</span></label
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
          >Durata luarii medicamentului <span class="text-red-500">*</span></label
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
          >Forma luarii medicamentului <span class="text-red-500">*</span></label
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
        <label for="route" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Calea de administrare a medicamentului <span class="text-red-500">*</span></label
        >
        <div class="w-full md:w-3/4">
          <Select
            name="route"
            :options="routes"
            placeholder="Calea de administrare"
            fluid
            class="w-full md:w-1/3"
          />
          <Message
            v-if="$form.route?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.route.error.message }}</Message
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
          :loading="isSubmitting"
          type="submit"
        />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
/**
 * @file AddMedication.vue
 * @description Component for adding a new medication. Displays a dialog with a form to input medication details,
 * which then sends a request to the backend to add the medication.
 */
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import { format } from 'date-fns'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {Array} forms - List of medication forms to choose from.
 * @prop {Array} routes - List of medication routes to choose from.
 */
const props = defineProps({
  displayDialog: Boolean,
  forms: Array,
  routes: Array,
})

/**
 * @emit {Function} add - Emits the 'add' event with the new medication data.
 * @emit {Function} close - Emits the 'close' event to close the dialog.
 */
const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)
const errorMessage = ref('')
const isSubmitting = ref(false)

const dosageUnits = ref([
  'capsula',
  'IU',
  'mL',
  'tableta',
  'g',
  'mg',
  'ug',
  'mcg',
  'PUFF',
  'Altele',
])
const frequency = ref(['pe zi', 'pe saptamana', 'pe luna'])

const initialValues = ref({
  name: '',
  dosage: '',
  dosageUnits: dosageUnits.value[0],
  frequencyChoice: '',
  frequencyValue: 0,
  frequencyUnits: frequency.value[0],
  datePrescribed: null,
  duration: 0,
  notes: '',
  form: props.forms[0],
  route: props.routes[0],
  timeOfDay: '',
})

const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele medicamentului este obligatoriu.'),
    dosage: z.string().nonempty('Doza medicamentului este obligatorie.'),
    frequencyValue: z
      .number('Frecventa luarii medicamentului trebuie sa fie un numar.')
      .int()
      .positive('Frecventa luarii medicamentului trebuie sa fie un numar pozitiv.')
      .optional(),
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
    timeOfDay: z.string().optional(),
    form: z.string().nonempty('Forma medicamentului este obligatorie.'),
    route: z.string().nonempty('Calea de administrare a medicamentului este obligatorie.'),
    dosageUnits: z.string().optional(),
    frequencyUnits: z.string().optional(),
    frequencyChoice: z.string().nonempty('Alege o optiune pentru frecventa.'),
  }),
)

/**
 * @description Sends a POST request to the backend to add a new medication with the provided details.
 * @param {Object} medicationDetails - The details of the medication to be added.
 */
const addMedication = async (medicationDetails) => {
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    let formattedDate = format(medicationDetails.datePrescribed, 'yyyy-MM-dd')

    let formattedFrequency = () => {
      switch (medicationDetails.frequencyChoice) {
        case 'standard':
          return medicationDetails.frequencyValue + ' ' + medicationDetails.frequencyUnits
        case 'alternativ':
          return (
            medicationDetails.frequencyValue +
            ' la fiecare 2 ' +
            medicationDetails.frequencyUnits.split(' ')[1]
          )
        case 'asNeeded':
          return 'la nevoie'
        case 'continuu':
          return 'continuu'
      }
    }

    const response = await api.post('me/medications', {
      name: medicationDetails.name,
      dosage: medicationDetails.dosage + medicationDetails.dosageUnits,
      frequency: formattedFrequency(),
      date_prescribed: formattedDate,
      duration_days: medicationDetails.duration,
      notes: medicationDetails.notes,
      form: medicationDetails.form,
      route: medicationDetails.route,
      time_of_day: medicationDetails.timeOfDay,
    })

    emit('add', response.data)
    emit('close')
  } catch (error) {
    console.error('Error adding medication:', error)
    errorMessage.value = error.response?.data?.detail || 'A apărut o eroare la adăugarea medicamentului. Vă rugăm să încercați din nou.'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * @description Handles the form submission event. Validates the form and calls addMedication if valid.
 * @param {Object} e - The form submission event object.
 */
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
