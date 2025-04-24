<template>
  <Dialog
    v-model:visible="displayShareDialog"
    modal
    header="Creeaza un link de partajare"
    @hide="emit('close')"
  >
    <div class="card flex justify-center">
      <Stepper value="1" class="basis-[50rem]" linear>
        <StepList>
          <Step value="1">Creeaza link-ul de partajare</Step>
          <Step value="2">Alege ce vrei sa partajezi</Step>
          <Step value="3">Partajeaza link-ul cu doctorul</Step>
        </StepList>
        <StepPanels>
          <!-- First panel of the stepper. Contains the PIN and expiration time components. -->
          <StepPanel v-slot="{ activateCallback }" value="1">
            <div class="flex flex-col items-center justify-center gap-4">
              <h1 class="font-bold">Alege un PIN pentru link-ul de partajare</h1>
              <InputOtp v-model="pin" :length="6" :invalid="pinValidation.error ? true : false" />
              <Message v-if="pinValidation.error" severity="error" variant="simple" size="small">{{
                pinValidation.error
              }}</Message>

              <p class="text-sm text-surface-500 dark:text-surface-400">
                Acest PIN va fi folosit pentru a accesa link-ul de partajare.
              </p>

              <!-- Expiration time selection slider -->
              <div class="flex flex-col gap-4 mt-4">
                <h1 class="font-bold">Alege duratia link-ului de partajare</h1>
                <div class="flex justify-between items-center">
                  <span>
                    {{ time }} {{ time > 1 ? selectedOption : selectedOption.replace('e', 'ă') }}
                  </span>
                  <SelectButton :options="options" v-model="selectedOption" class="w-1/2" />
                </div>
                <Slider
                  v-model="time"
                  :min="1"
                  :max="selectedOption === 'Ore' ? 24 : 120"
                  :step="1"
                  class="w-full"
                />
                <div class="flex justify-between items-center">
                  <Button
                    label="1 ora"
                    @click="((time = 1), (selectedOption = 'Ore'))"
                    class="p-button-outlined mr-2"
                  />
                  <Button
                    label="2 ore"
                    @click="((time = 2), (selectedOption = 'Ore'))"
                    class="p-button-outlined mr-2"
                  />
                  <Button
                    label="30 min"
                    @click="((time = 30), (selectedOption = 'Minute'))"
                    class="p-button-outlined mr-2"
                  />
                </div>
              </div>
            </div>
            <div class="flex pt-6 justify-end">
              <Button
                label="Next"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="
                  () => {
                    if (pinValidation.success) {
                      apiError = null
                      activateCallback('2')
                    }
                  }
                "
              />
            </div>
          </StepPanel>

          <!-- Second panel of the stepper. Contains the component that allows the selection of records that will be share with a doctor -->
          <StepPanel v-slot="{ activateCallback }" value="2">
            <div class="flex flex-col">
              <Message v-if="apiError" severity="error" class="mb-3">
                {{ apiError }}
              </Message>
              <RecordsTable
                :records="props.records"
                @back="activateCallback('1')"
                @next="
                  async (selectedChildRows) => {
                    const result = await createShareLink(selectedChildRows)
                    if (result) {
                      activateCallback('3')
                    } else {
                      // Error is already displayed via apiError ref
                    }
                  }
                "
              />
            </div>
          </StepPanel>

          <!-- Third panel of the stepper. Contains the link and PIN that were generated in the previous step. -->
          <!-- The link and PIN are displayed to the user, and they can be copied to the clipboard. -->
          <StepPanel v-slot="{ activateCallback }" value="3">
            <div class="flex flex-col items-center justify-center gap-5 p-2">
              <div class="text-center">
                <i class="pi pi-check-circle text-5xl text-green-500 mb-3"></i>
                <h1 class="text-2xl font-bold mb-2">
                  Link-ul de partajare a fost creat cu succes!
                </h1>
                <p class="text-sm text-surface-500 dark:text-surface-400">
                  Poți transmite aceste informații doctorului tău pentru a accesa datele tale
                  medicale
                </p>
              </div>

              <div class="w-full p-2">
                <div class="flex flex-col mb-4 justify-center items-center">
                  <span class="font-bold mb-1 text-2xl">Link de acces:</span>
                  <div>
                    <Button
                      icon="pi pi-copy"
                      variant="text"
                      aria-label="copy"
                      severity="secondary"
                      @click="copyContent()"
                    />
                    <span class="text-xl text-surface-500 dark:text-surface-400">
                      http://localhost:5173/share/{{ linkData?.code }}
                    </span>
                    <Message v-if="copySuccess" severity="success" class="mt-2">
                      Link-ul a fost copiat în clipboard!
                    </Message>
                  </div>
                </div>

                <div class="flex flex-col mb-4 justify-center items-center">
                  <span class="font-bold text-2xl mb-1">PIN de acces:</span>
                  <div class="flex gap-2 items-center">
                    <div
                      class="flex gap-1 p-2 bg-surface-100 dark:bg-surface-800 rounded-md w-full justify-center"
                    >
                      <span
                        v-for="(digit, index) in pin"
                        :key="index"
                        class="inline-flex items-center justify-center w-10 h-10 rounded-md bg-surface-0 dark:bg-surface-900 border-1 font-bold"
                      >
                        {{ digit }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="mb-4 flex justify-center items-center">
                  <Message
                    severity="warn"
                    :closable="false"
                    class="flex items-center w-1/2"
                    icon="pi pi-info-circle"
                  >
                    <span class="font-bold">
                      Link-ul va expira la:
                      {{
                        linkData?.expiration_time
                          ? format(new Date(linkData.expiration_time), 'dd MMM yyyy - HH:mm')
                          : ''
                      }}
                    </span>
                  </Message>
                </div>
              </div>

              <div class="flex gap-3 mt-3">
                <Button icon="pi pi-envelope" label="Trimite pe email" class="p-button-outlined" />
                <Button icon="pi pi-qrcode" label="Genereaza QR code" class="p-button-outlined" />
              </div>
            </div>
            <div class="pt-6">
              <Button
                label="Back"
                severity="secondary"
                icon="pi pi-arrow-left"
                @click="activateCallback('2')"
              />
            </div>
          </StepPanel>
        </StepPanels>
      </Stepper>
    </div>
  </Dialog>
</template>

<script setup>
/**
 * @file CreateShareLink.vue
 * @description This component is responsible for creating a shareable link for the user's medical records.
 * It allows the user to select a PIN, duration for which the link will be valid, and the records they want to share.
 * Once the link is created, it displays the link and PIN to the user.
 * The user can then copy the link and PIN to share with their doctor.
 */
import RecordsTable from '../share/RecordsTable.vue'
import api from '@/services/api'
import { computed, ref } from 'vue'
import { z } from 'zod'
import { format, formatISO } from 'date-fns'

/**
 * @prop {Boolean} displayDialog - Controls the visibility of the dialog.
 * @prop {Object} records - The medical records to be shared. Will contain all the records that the user has, passed from the dashboard page.
 */
const props = defineProps({
  displayDialog: Boolean,
  records: Object,
})

/**
 * @emit {Function} close - Emits an event to close the dialog.
 */
const emit = defineEmits(['close'])

const displayShareDialog = ref(props.displayDialog)
const pin = ref('')
const time = ref(1)
const options = ref(['Ore', 'Minute'])
const selectedOption = ref('Ore')
const linkData = ref()
const apiError = ref(null)
const copySuccess = ref(false)

/**
 * @description Validates the PIN input using the given Zod schema.
 * @returns {Object} - An object containing the validation result and error message if any.
 * 
 */
const pinValidation = computed(() => {
  const pinSchema = z.string().length(6, { message: 'PIN-ul trebuie sa contina 6 caractere' })
  const result = pinSchema.safeParse(pin.value)

  return {
    success: result.success,
    error: result.success ? null : result.error.format()._errors[0],
  }
})

/**
 * @description Function to create a shareable link for the selected medical records. Takes in the selected child rows from the RecordsTable component, and sends a POST request to the API to create the link.
 *
 * @param selectedChildRows {Array} - The selected child rows from the RecordsTable component.
 */
const createShareLink = async (selectedChildRows) => {

  const sharedItems = processSharedItems(selectedChildRows)
  const timeInMinutes = selectedOption.value === 'Ore' ? time.value * 60 : time.value

  try {
    const response = await api.post('/share/create', {
      token_length: timeInMinutes,
      pin: pin.value,
      shared_items: sharedItems,
    })

    linkData.value = response.data
    return true
  } catch (error) {
    console.error('Error creating share link:', error)
    apiError.value = error.response?.data?.detail || 
                     'A apărut o eroare la crearea link-ului de partajare. Încearcă din nou.'
    return false
  }
}

/**
 * Helper function that processes the selected child rows from RecordsTable into their respective types (can't be done in records table as there is no info on type from selected child rows) and formats the date fields to ISO format. Data will be used to create the share link.
 * @param selectedChildRows {Array} - The selected child rows from the RecordsTable component.
 * @returns {Object} - An object containing the processed shared items, with they type as the key and the records array as the value.
 */
const processSharedItems = (selectedChildRows) => {
  const sharedItems = {}

  for (const [type, records] of Object.entries(props.records)) {
    // Compare the selected child rows with the given records by the dashboard page to 
    const selectedRecords = records
      .filter((record) => {
        return selectedChildRows.some((selected) => selected.id === record.id)
      })
      .map((record) => {
        const processedRecord = { ...record }

        for (const key in processedRecord) {
          // Check if the key is a date field and not an original date field. Original date fields are string fields, but not formatted in the ISO format so using the other date field to create an ISO string to pass to the backend.
          if (key.includes('date') && !key.includes('original')) {
            const date = processedRecord[key]

            // Formatting the date to ISO format
            processedRecord[key] = formatISO(date, {
              representation: 'date',
            })
          }
        }
        return processedRecord
      })

    if (selectedRecords.length > 0) {
      sharedItems[type] = selectedRecords
    }
  }

  return sharedItems
}

/**
 * @description Function to copy the generated share link to the clipboard.
 * Uses the Clipboard API to write the text to the clipboard.
 * Handles any errors that may occur during the copy process.
 */
const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(`http://localhost:5173/share/${linkData.value.code}`)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('Failed to copy: ', err)
  }
}
</script>
