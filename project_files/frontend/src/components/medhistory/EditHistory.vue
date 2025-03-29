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
  
      <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="name" class="font-semibold text-sm md:text-base w-full md:w-1/4">Descriere</label>
          <div class="w-full md:w-3/4 flex flex-col">
            <InputText name="name" class="w-full md:w-3/4" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.name?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.name.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="doctor_name" class="font-semibold text-sm md:text-base w-full md:w-1/4">Numele doctorului</label>
          <div class="w-full md:w-3/4 flex flex-col">
            <InputText name="doctor_name" class="w-full md:w-3/4" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.doctor_name?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.doctor_name.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="place" class="font-semibold text-sm md:text-base w-full md:w-1/4">Locație</label>
          <div class="w-full md:w-3/4 flex flex-col">
            <InputText name="place" class="w-full md:w-3/4" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.place?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-xs md:text-sm mt-1"
            >{{ $form.place.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="date_consultation" class="font-semibold text-sm md:text-base w-full md:w-1/4">Data consultării</label>
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
            >{{ $form.date_consultation.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="category" class="font-semibold text-sm md:text-base w-full md:w-1/4">Categorie</label>
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
            >{{ $form.category.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-6">
          <label for="subcategory" class="font-semibold text-sm md:text-base w-full md:w-1/4">Subcategorie</label>
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
            >{{ $form.subcategory.error.message }}</Message>
          </div>
        </div>
  
        <div class="flex flex-col md:flex-row md:items-start gap-2 md:gap-6 mb-6">
          <label for="notes" class="font-semibold text-sm md:text-base w-full md:w-1/4 pt-2">Note</label>
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
            >{{ $form.notes.error.message }}</Message>
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
          />
        </div>
      </Form>
    </Dialog>
  </template>
  
  <script setup>
  import Dialog from 'primevue/dialog'
  import InputText from 'primevue/inputtext'
  import { Form } from '@primevue/forms'
  import DatePicker from 'primevue/datepicker'
  import Message from 'primevue/message'
  import Button from 'primevue/button'
  
  import Select from 'primevue/select'
  import Textarea from 'primevue/textarea'
  import { parse } from 'date-fns'
  
  import { z } from 'zod'
  import { zodResolver } from '@primevue/forms/resolvers/zod'
  import api from '@/services/api'
  import { ref, computed } from 'vue'
  
  const props = defineProps({
    displayDialog: Boolean,
    medicalHistory: Object,
    categories: Array,
    subcategories: Array,
  })
  
  const emit = defineEmits(['edit', 'close'])
  const maxDate = ref(new Date())
  const displayEditDialog = ref(props.displayDialog)
  
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
      notes: props.medicalHistory.notes || '',
    }
  })
  
  const resolver = zodResolver(
    z.object({
      name: z.string().nonempty('Numele înregistrării este obligatoriu.'),
      doctor_name: z.string().nonempty('Numele medicului este obligatoriu.'),
      place: z.string().optional(),
      date_consultation: z
        .date({ message: 'Data consultării este obligatorie.' })
        .nullable()
        .refine((value) => value !== null, {
          message: 'Data consultării este obligatorie.',
        })
        .refine((value) => value === null || value <= new Date(), {
          message: 'Data consultării nu poate fi în viitor.',
        }),
      category: z.string().nonempty('Categoria este obligatorie.'),
      subcategory: z.string().nonempty('Subcategoria este obligatorie.'),
      notes: z.string().optional(),
    }),
  )
  
  const updateMedicalHistory = async (medicalHistoryDetails) => {
    try {
      let formattedDate = null
  
      // Format the date as yyyy-mm-dd
      if (medicalHistoryDetails.date_consultation instanceof Date) {
        const [day, month, year] = medicalHistoryDetails.date_consultation
          .toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit', year: 'numeric' })
          .split('.')
        formattedDate = `${year}-${month}-${day}`
      }
  
      if (!formattedDate) {
        console.error('Date is required but not properly formatted')
        return
      }
  
      const response = await api.put(`me/medicalhistory/${props.medicalHistory.id}`, {
        name: medicalHistoryDetails.name,
        doctor_name: medicalHistoryDetails.doctor_name,
        place: medicalHistoryDetails.place || null,
        date_consultation: formattedDate,
        category: medicalHistoryDetails.category,
        subcategory: medicalHistoryDetails.subcategory,
        notes: medicalHistoryDetails.notes || null,
      })
  
      emit('edit', response.data.medicalhistory)
      emit('close')
    } catch (error) {
      console.error('Error updating medical history:', error)
    }
  }
  
  
  
  const onFormSubmit = (e) => {
    if (!e.valid) {
      console.error('Error updating medical history: ', e.errors)
      return
    }
  
    updateMedicalHistory(e.values)
  }
  </script>