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
              <InputOtp v-model="pin" :length="6" />

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
                @click="activateCallback('2')"
              />
            </div>
          </StepPanel>
          <StepPanel v-slot="{ activateCallback }" value="2">
            <div class="flex flex-col">
              <div
                class="border-2 border-dashed border-surface-200 dark:border-surface-700 rounded bg-surface-50 dark:bg-surface-950 flex-auto flex justify-center items-center font-medium"
              >
                Content II
              </div>
            </div>
            <div class="flex pt-6 justify-between">
              <Button
                label="Back"
                severity="secondary"
                icon="pi pi-arrow-left"
                @click="activateCallback('1')"
              />
              <Button
                label="Next"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="activateCallback('3')"
              />
            </div>
          </StepPanel>
          <StepPanel v-slot="{ activateCallback }" value="3">
            <div class="flex flex-col">
              <div
                class="border-2 border-dashed border-surface-200 dark:border-surface-700 rounded bg-surface-50 dark:bg-surface-950 flex-auto flex justify-center items-center font-medium"
              >
                Content III
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
import { ref } from 'vue'

const props = defineProps({
  displayDialog: Boolean,
})

const emit = defineEmits(['close'])

const displayShareDialog = ref(props.displayDialog)
const pin = ref(null)
const time = ref(1)
const options = ref(['Ore', 'Minute'])
const selectedOption = ref('Ore')
</script>
