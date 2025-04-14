<template>
  <Dialog
    v-model:visible="displayEditDialog"
    modal
    class="w-full md:w-3/4 lg:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Actualizeaza medicament</span>
      </div>
    </template>

    <span class="text-gray-500 dark:text-gray-400 block mb-4 md:mb-8 text-sm md:text-base">
      Actualizeaza informatia pentru medicamentul selectat.
    </span>

    <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
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

      <div class="flex flex-col gap-4 md:gap-6 mb-6">
        <div class="flex flex-row gap-4 items-center">
          <label class="font-semibold text-sm md:text-base"> Tipul frecventei </label>
          <RadioButtonGroup name="frequencyChoice" class="flex flex-row">
            <div class="flex items-center gap-2 ml-2">
              <RadioButton value="standard" inputId="standard" />
              <label for="standard" class="text-sm md:text-base cursor-pointer">Standard</label>
            </div>

            <div class="flex items-center gap-2 ml-2">
              <RadioButton value="alternativ" inputId="alternativ" />
              <label for="alternativ" class="text-sm md:text-base cursor-pointer">Alternativ</label>
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
            <Message
              v-if="$form.timeOfDay?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm"
            >
              {{ $form.timeOfDay.error.message }}</Message
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
        <label for="route" class="font-semibold text-sm md:text-base w-full md:w-1/4"
          >Calea de administrare a medicamentului</label
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
          type="submit"
        />
      </div>
    </Form>
  </Dialog>
</template>

<script setup>
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref, computed } from 'vue'
import { parse, format } from 'date-fns'

const props = defineProps({
  displayDialog: Boolean,
  medication: Object,
  forms: Array,
  routes: Array,
})

const emit = defineEmits(['edit', 'close'])
const maxDate = ref(new Date())
const displayEditDialog = ref(props.displayDialog)

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

const initialValues = computed(() => {
  if (!props.medication) return {}

  let dosageValue = ''
  let dosageUnit = ''
  let frequencyChoice = ''

  if (props.medication.dosage) {
    // Separate number and string part
    const dosageMatch = props.medication.dosage.match(/^(\d+)(.*)$/)
    if (dosageMatch) {
      dosageValue = dosageMatch[1]
      dosageUnit = dosageMatch[2].trim()
    } else {
      dosageValue = props.medication.dosage
    }
  }

  let frequencyValue = 1
  let frequencyUnit = ''

  if (props.medication.frequency) {
    // Separate number and string part
    if (props.medication.frequency.includes('la nevoie')) {
      frequencyValue = 0
      frequencyChoice = 'asNeeded'
    } else if (props.medication.frequency.includes('continuu')) {
      frequencyValue = 0
      frequencyChoice = 'continuu'
    } else {
      const patterns = [
        // 2 pe zi/saptamana/luna
        /^(\d+)\s*(pe\s*(zi|saptamana|luna))$/,
        // 1 la fiecare 2 zi
        /^(\d+)\s*la\s*fiecare\s*(\d+)\s*(zi|saptamana|luna)$/,
      ]

      let matched = false
      for (const pattern of patterns) {
        const match = props.medication.frequency.match(pattern)
        if (match) {
          matched = true
          if (props.medication.frequency.includes('fiecare')) {
            // Handle "la fiecare X zi" pattern
            frequencyChoice = 'alternativ'
            frequencyValue = parseInt(match[1]) // Changed to match[2] to get interval value
            frequencyUnit = 'pe ' + match[3]
          } else {
            // Handle regular "pe zi/saptamana/luna" pattern
            frequencyChoice = 'standard'
            frequencyValue = parseInt(match[1])
            frequencyUnit = match[2]
          }
          break
        }
      }

      if (!matched) {
        // Default fallback
        frequencyValue = 1
        frequencyUnit = 'pe zi'
        console.warn('Unrecognized frequency pattern:', props.medication.frequency)
      }
    }
  }

  const prescriptionDate = parse(props.medication.date_prescribed, 'dd-MM-yyyy', new Date())

  return {
    name: props.medication.name,
    dosage: dosageValue,
    dosageUnits: dosageUnit,
    frequencyValue: frequencyValue, //
    frequencyUnits: frequencyUnit,
    datePrescribed: prescriptionDate,
    duration: props.medication.duration_days,
    notes: props.medication.notes,
    form: props.medication.form,
    route: props.medication.route,
    timeOfDay: props.medication.time_of_day,
    frequencyChoice: frequencyChoice,
  }
})

const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele medicamentului este obligatoriu.'),
    dosage: z.string().nonempty('Doza medicamentului este obligatorie.'),
    datePrescribed: z
      .date({ message: 'Data prescrierii medicamentului este obligatorie.' })
      .refine((value) => value < new Date(), {
        message: 'Data prescrierii medicamentului nu poate fi in viitor.',
      }),
    duration: z
      .number('Durata tratamentului trebuie sa fie un numar.')
      .int()
      .positive('Durata tratamentului trebuie sa fie un numar pozitiv.')
      .optional(),
    notes: z.string().optional(),
    form: z.string().nonempty('Forma medicamentului este obligatorie.'),
    dosageUnits: z.string().nonempty('Unitatea de masura a dozei este obligatorie.'),
    frequencyUnits: z.string().optional(),
    frequencyValue: z
      .number('Frecventa luarii medicamentului trebuie sa fie un numar.')
      .int()
      .positive('Frecventa luarii medicamentului trebuie sa fie un numar pozitiv.')
      .optional(),
    frequencyChoice: z.string().nonempty('Alege o optiune pentru frecventa.'),
    timeOfDay: z.string().optional(),
    route: z.string().nonempty('Calea de administrare a medicamentului este obligatorie.'),
  }),
)

const updateMedication = async (medicationDetails) => {
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

    const response = await api.patch(`/me/medications/${props.medication.id}`, {
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

    emit('edit', response.data.medication)
    emit('close')
  } catch (error) {
    console.error('Error updating medication:', error)
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
    console.error('Error updating medication: ', e.errors)
    return
  }

  console.log('Form values:', e.values)
  console.log('Form states:', e.states)
  console.log('Initial values:', {...initialValues.value})

  updateMedication(e.values)
}
</script>
