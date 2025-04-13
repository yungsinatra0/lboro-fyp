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
                    const result = await createShareLink(selectedParentRows, selectedChildRows);
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
            <div class="flex flex-col">
              <h1 class="font-bold">Link-ul de partajare a fost creat cu succes!</h1>
              <p class="text-sm text-surface-500 dark:text-surface-400">
                Link-ul de partajare este: <strong> http://localhost:5173/share/{{ linkData?.code }}</strong>
              </p>
              <p class="text-sm text-surface-500 dark:text-surface-400">
                PIN-ul este: <strong>{{ pin }}</strong>
              </p>
              <p class="text-sm text-surface-500 dark:text-surface-400">
                Acest link va expira la {{ linkData?.expiration_time ? format(linkData.expiration_time, "HH:mm:ss") : '' }}
              </p>
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
</script>
