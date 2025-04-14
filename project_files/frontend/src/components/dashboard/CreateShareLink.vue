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
                      activateCallback('2')
                    } else {
                      // Will add something here later
                    }
                  }
                "
              />
            </div>
          </StepPanel>
          <StepPanel v-slot="{ activateCallback }" value="2">
            <div class="flex flex-col">
              <RecordsTable
                :records="props.records"
                @back="activateCallback('1')"
                @next="
                  async (selectedParentRows, selectedChildRows) => {
                    const result = await createShareLink(selectedParentRows, selectedChildRows)
                    if (result) {
                      activateCallback('3')
                    } else {
                      // Will add something here later
                    }
                  }
                "
              />
            </div>
          </StepPanel>
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
import Dialog from 'primevue/dialog'
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepPanels from 'primevue/steppanels'
import SelectButton from 'primevue/selectbutton'
import Slider from 'primevue/slider'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import InputOtp from 'primevue/inputotp'
import Button from 'primevue/button'
import Message from 'primevue/message'
import RecordsTable from '../share/RecordsTable.vue'
import api from '@/services/api'
import { computed, ref } from 'vue'
import { z } from 'zod'
import { format } from 'date-fns'

const props = defineProps({
  displayDialog: Boolean,
  records: Object,
})

const emit = defineEmits(['close'])

const displayShareDialog = ref(props.displayDialog)
const pin = ref('')
const time = ref(1)
const options = ref(['Ore', 'Minute'])
const selectedOption = ref('Ore')
const linkData = ref()

const pinValidation = computed(() => {
  const pinSchema = z.string().length(6, { message: 'PIN-ul trebuie sa contina 6 caractere' })
  const result = pinSchema.safeParse(pin.value)

  return {
    success: result.success,
    error: result.success ? null : result.error.format()._errors[0],
  }
})

const createShareLink = async (selectedParentRows, selectedChildRows) => {
  console.log('Received Parent Rows:', selectedParentRows)
  console.log('Received Child Rows:', selectedChildRows)

  const sharedItems = processSharedItems(selectedParentRows, selectedChildRows)
  console.log('Shared Items:', sharedItems)

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
    return false
  }
}

const processSharedItems = (selectedParentRows, selectedChildRows) => {
  const sharedItems = []

  selectedParentRows.forEach((parentRow) => {
    for (const item of parentRow.items) {
      const itemId = item.id
      // check the records in parentRow object versus the ones selected in the selectedChildRows
      const selectedChildRow = selectedChildRows.some((childRow) => childRow.id === itemId)
      if (selectedChildRow) {
        sharedItems.push({
          item_type: parentRow.type,
          item_id: itemId,
        })
      }
    }
  })

  return sharedItems
}

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(`http://localhost:5173/share/${linkData.value.code}`)
  } catch (err) {
    console.error('Failed to copy: ', err)
  }
}
</script>
