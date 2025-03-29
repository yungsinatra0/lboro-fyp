<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    header="Adauga o înregistrare medicală"
    class="w-full md:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">
        <span class="font-bold whitespace-nowrap text-2xl">Înregistrare medicală nouă</span>
      </div>
    </template>
    <span class="text-surface-500 dark:text-surface-400 block mb-8"
      >Adaugă informații pentru o nouă înregistrare medicală.</span
    >
    <Form v-slot="$form" :initialValues="initialValues" @submit="onFormSubmit" :resolver="resolver">
      <div class="flex items-center gap-4 mb-4">
        <label for="name" class="font-semibold w-24">Descriere</label>
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
        <label for="doctor_name" class="font-semibold w-24">Numele doctorului</label>
        <InputText name="doctor_name" class="flex w-1/2" autocomplete="off" type="text" fluid />
        <Message
          v-if="$form.doctor_name?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.doctor_name.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="place" class="font-semibold w-24">Locație</label>
        <InputText name="place" class="flex w-1/2" autocomplete="off" type="text" fluid />
        <Message
          v-if="$form.place?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.place.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="date_consultation" class="font-semibold w-24">Data consultării</label>
        <DatePicker
          name="date_consultation"
          dateFormat="dd/mm/yy"
          placeholder="Data"
          showIcon
          fluid
          :maxDate="maxDate"
        />
        <Message
          v-if="$form.date_consultation?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.date_consultation.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="category" class="font-semibold w-24">Categorie</label>
        <Select
          name="category"
          :options="categories"
          placeholder="Selectează categoria"
          class="flex w-1/2"
          fluid
        />
        <Message
          v-if="$form.category?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.category.error.message }}</Message
        >
      </div>
      <div class="flex items-center gap-4 mb-4">
        <label for="subcategory" class="font-semibold w-24">Subcategorie</label>
        <Select
          name="subcategory"
          :options="subcategories"
          placeholder="Selectează subcategoria"
          class="flex w-1/2"
          fluid
        />
        <Message
          v-if="$form.subcategory?.invalid"
          severity="error"
          size="small"
          variant="simple"
          class="text-rose-600 text-sm"
          >{{ $form.subcategory.error.message }}</Message
        >
      </div>
      <div class="flex gap-4 mb-4">
        <label for="notes" class="font-semibold">Notite</label>
        <Textarea
          name="notes"
          class="w-full md:w-2/4"
          autocomplete="off"
          type="text"
          fluid
          rows="3"
          placeholder="Adaugă note sau observații"
        />
      </div>
      <FileUpload
        name="file"
        mode="basic"
        @select="onSelect"
        :multiple="false"
        :custom-upload="true"
        :maxFileSize="10000000"
        :choose-label="`Alege documentul medical`"
        :upload-label="`Încarcă`"
        :cancel-label="`Anulează`"
      >
        <template #empty>
          <span>Adaugă un document medical (opțional).</span>
        </template>
      </FileUpload>
      <div class="shrink-0 pt-3 px-5 pb-2 flex justify-end gap-2">
        <Button
          label="Anulează"
          outlined
          severity="danger"
          @click="emit('close')"
          autofocus
          type="button"
        />
        <Button label="Salvează" severity="success" autofocus type="submit" />
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
import FileUpload from 'primevue/fileupload'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { parse } from 'date-fns'
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'

const props = defineProps({
  displayDialog: Boolean,
  categories: Array,
  subcategories: Array,
})

const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)
const uploadedFile = ref(null)

const initialValues = ref({
  name: '',
  doctor_name: '',
  place: '',
  date_consultation: null,
  category: [],
  subcategory: [],
  notes: '',
})

const resolver = zodResolver(
  z.object({
    name: z.string().nonempty('Numele înregistrării este obligatoriu.'),
    doctor_name: z.string().nonempty('Numele medicului este obligatoriu.'),
    place: z.string().optional(),
    date_consultation: z
      .date({ message: 'Data consultării este obligatorie.' })
      .refine((value) => value <= new Date(), {
        message: 'Data consultării nu poate fi în viitor.',
      }),
    category: z.string().nonempty('Categoria este obligatorie.'),
    subcategory: z.string().nonempty('Subcategoria este obligatorie.'),
    notes: z.string().optional(),
  }),
)

const addMedicalHistory = async (medicalHistoryDetails) => {
  try {
    let formattedDate = medicalHistoryDetails.date_consultation

    // Format the date as yyyy-mm-dd
    if (medicalHistoryDetails.date_consultation instanceof Date) {
      const [day, month, year] = medicalHistoryDetails.date_consultation
        .toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit', year: 'numeric' })
        .split('.')
      formattedDate = `${year}-${month}-${day}`
    }

    const response = await api.post('me/medicalhistory', {
      name: medicalHistoryDetails.name,
      doctor_name: medicalHistoryDetails.doctor_name,
      place: medicalHistoryDetails.place || null,
      date_consultation: formattedDate,
      category: medicalHistoryDetails.category,
      subcategory: medicalHistoryDetails.subcategory,
      notes: medicalHistoryDetails.notes || null,
    })

    let hasFile = false

    if (uploadedFile.value) {
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      await api.post(`upload/medicalhistory/${response.data.medicalhistory.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      hasFile = true
    }

    emit('add', {
      ...response.data.medicalhistory,
      original_date_consultation: response.data.date_consultation,
      date_consultation: parse(response.data.date_consultation, 'dd-MM-yyyy', new Date()),
      file: hasFile,
    })
    emit('close')
  } catch (error) {
    console.error('Error in medical history operation:', error)
  }
}

const onSelect = (event) => {
  uploadedFile.value = event.files[0]
  console.log(uploadedFile.value)
}

const onFormSubmit = (e) => {
  if (!e.valid) {
    console.error('Error adding medical history: ', e.errors)
    return
  }

  addMedicalHistory(e.values)
}
</script>
