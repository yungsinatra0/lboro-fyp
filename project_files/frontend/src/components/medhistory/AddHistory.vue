<!-- TODO: Make it more mobile friendly, especially the confirming of lab results part. -->
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
    <div v-if="!loadingState && !extractionResult">
      <span class="text-surface-500 dark:text-surface-400 block mb-2"
        >Adaugă informații pentru o nouă înregistrare medicală.</span
      >
      <span class="text-rose-600 text-sm block mb-8">* Câmpurile marcate sunt obligatorii</span>
      <span v-if="formError" class="text-rose-600 text-sm block mb-8">{{ formError }}</span>
      <Form
        v-slot="$form"
        :initialValues="initialValues"
        @submit="onFormSubmit"
        :resolver="resolver"
      >
        <div class="flex items-center gap-4 mb-4">
          <label for="name" class="font-semibold w-24"
            >Descriere <span class="text-rose-600">*</span></label
          >
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
          <label for="doctor_name" class="font-semibold w-24"
            >Numele doctorului <span class="text-rose-600">*</span></label
          >
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
          <label for="category" class="font-semibold w-24"
            >Categorie <span class="text-rose-600">*</span></label
          >
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
        <div class="flex items-center gap-4 mb-4" v-if="$form.category?.value === 'Consultație'">
          <label for="subcategory" class="font-semibold w-24">Subcategorie consultație</label>
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
        <div class="flex items-center gap-4 mb-4" v-if="$form.category?.value === 'Laborator'">
          <label for="labsubcategory" class="font-semibold w-24">Subcategorie laborator</label>
          <Select
            name="labsubcategory"
            :options="labsubcategories"
            placeholder="Selectează subcategoria"
            class="flex w-1/2"
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
        <div class="flex items-center gap-4 mb-4" v-if="$form.category?.value === 'Laborator'">
          <label for="extract" class="font-semibold w-24">Extrage date laborator cu AI?</label>
          <ToggleSwitch name="extract" />
          <Message
            v-if="$form.extract?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.extract.error.message }}</Message
          >
        </div>
        <div class="flex items-center gap-4 mb-4">
          <label for="date_consultation" class="font-semibold w-24"
            >Data efectuării<span class="text-rose-600">*</span></label
          >
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
    </div>
    <div v-else>
      <div class="flex flex-col items-center p-4" v-if="!extractionResult">
        <ProgressSpinner />
        <p class="mt-3">Se procesează documentul...</p>
      </div>

      <div v-else class="flex flex-col items-center p-4">
        <div v-if="!extractSuccess">
          <DataTable
            :value="extractionResult"
            v-model:editingRows="editingRows"
            class="w-full"
            :rows="10"
            editMode="row"
            paginator
            dataKey="test_name"
            @row-edit-save="onRowEditSave"
            v-model:filters="filters"
            :globalFilterFields="['test_name', 'test_code']"
          >
            <template #header>
              <h2 class="m-0">Analizati rezultatele extrase si schimbati daca sunt gresite</h2>
              <div class="flex justify-end">
                <IconField>
                  <InputIcon>
                    <i class="pi pi-search" />
                  </InputIcon>
                  <InputText
                    size="small"
                    v-model="filters['global'].value"
                    placeholder="Cauta..."
                  />
                </IconField>
              </div>
            </template>
            <Column v-for="col of columns" :key="col.field" :field="col.field" :header="col.header">
              <template #editor="{ data, field }">
                <InputText v-model="data[field]" class="w-full" fluid />
              </template>
            </Column>
            <!-- TODO: Add a way to add/remove additional lab results if they weren't properly extracted by LLM -->
            <Column
              :rowEditor="true"
              style="width: 10%; min-width: 8rem"
              bodyStyle="text-align:center"
            />
          </DataTable>
          <div class="shrink-0 pt-3 flex justify-end gap-2">
            <Button
              label="Salvează"
              severity="success"
              @click="addExtractedLab()"
              autofocus
              type="button"
            />
            <Button
              label="Anulează"
              outlined
              severity="danger"
              @click="emit('close')"
              autofocus
              type="button"
            />
          </div>
        </div>
        <div v-else class="flex flex-col items-center p-8">
          <i class="pi pi-check-circle text-6xl text-green-500 mb-4" />
          <Message severity="success" class="mb-6 text-lg">
            Rezultatele au fost extrase cu succes! Acestea sunt acum disponibile in sectiunea de
            laborator.
          </Message>
          <Button
            label="Vezi rezultatele"
            severity="success"
            class="px-6 py-3 text-lg"
            @click="
              () => {
                router.push({ path: '/laborator' })
                emit('close')
              }
            "
            autofocus
            type="button"
          />
        </div>
      </div>
    </div>
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
import ToggleSwitch from 'primevue/toggleswitch'
import ProgressSpinner from 'primevue/progressspinner'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { FilterMatchMode } from '@primevue/core/api'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import { parse, format } from 'date-fns'
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import api from '@/services/api'
import { ref } from 'vue'
import router from '@/router'

const props = defineProps({
  displayDialog: Boolean,
  categories: Array,
  subcategories: Array,
  labsubcategories: Array,
})

const emit = defineEmits(['add', 'close'])
const maxDate = ref(new Date())
const displayAddDialog = ref(props.displayDialog)
const loadingState = ref(false)
const extractionResult = ref(null)
const uploadedFile = ref(null)
const editingRows = ref([])
const labDetails = ref(null)
const formError = ref(null)
const extractSuccess = ref(false)
const columns = ref([
  { field: 'test_name', header: 'Test' },
  { field: 'test_code', header: 'Cod' },
  { field: 'value', header: 'Valoare' },
  { field: 'unit', header: 'Unitate' },
  { field: 'reference_range', header: 'Interval de referință' },
  { field: 'method', header: 'Metodă' },
])

const initialValues = ref({
  name: '',
  doctor_name: '',
  place: '',
  date_consultation: null,
  category: '',
  subcategory: '',
  labsubcategory: '',
  notes: '',
  extract: false,
})

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
    subcategory: z.string().optional(),
    labsubcategory: z.string().optional(),
    notes: z.string().optional(),
    extract: z.boolean().optional(),
  }),
)

const addMedicalHistory = async (medicalHistoryDetails) => {
  try {
    let formattedDate = format(medicalHistoryDetails.date_consultation, 'yyyy-MM-dd')

    const response = await api.post('me/medicalhistory', {
      name: medicalHistoryDetails.name,
      doctor_name: medicalHistoryDetails.doctor_name,
      place: medicalHistoryDetails.place || null,
      date_consultation: formattedDate,
      category: medicalHistoryDetails.category,
      subcategory:
        medicalHistoryDetails.category == 'Consultație' ? medicalHistoryDetails.subcategory : null,
      labsubcategory:
        medicalHistoryDetails.category == 'Laborator' ? medicalHistoryDetails.labsubcategory : null,
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

    if (medicalHistoryDetails.extract) {
      emit('add', {
        ...response.data.medicalhistory,
        original_date_consultation: response.data.medicalhistory.date_consultation,
        date_consultation: parse(
          response.data.medicalhistory.date_consultation,
          'dd-MM-yyyy',
          new Date(),
        ),
        file: hasFile,
      })

      labDetails.value = {
        medicalhistory_id: response.data.medicalhistory.id,
        date_collection: formattedDate,
      }

      loadingState.value = true

      const llm_response = await api.post(`/labtests/extract/${response.data.medicalhistory.id}`)

      extractionResult.value = JSON.parse(llm_response.data)

      loadingState.value = false
    } else {
      emit('add', {
        ...response.data.medicalhistory,
        original_date_consultation: response.data.medicalhistory.date_consultation,
        date_consultation: parse(
          response.data.medicalhistory.date_consultation,
          'dd-MM-yyyy',
          new Date(),
        ),
        file: hasFile,
      })
      emit('close')
    }
  } catch (error) {
    console.error('Error in medical history operation:', error)
    formError.value = error.response.data.detail
  }
}

const addExtractedLab = async () => {
  try {
    const response = await api.post('/me/labtests', {
      medicalhistory_id: labDetails.value.medicalhistory_id,
      date_collection: labDetails.value.date_collection,
      lab_tests: extractionResult.value.map((item) => ({
        name: item.test_name,
        code: item.test_code,
        value: item.value,
        unit: item.unit,
        reference_range: item.reference_range,
        method: item.method,
      })),
    })

    if (response.status === 200) {
      extractSuccess.value = true
    }
  } catch (error) {
    console.error('Error in adding extracted lab:', error)
  }
}

const onRowEditSave = (event) => {
  let { newData, index } = event

  extractionResult.value[index] = newData
}

const onSelect = (event) => {
  uploadedFile.value = event.files[0]
}

const onFormSubmit = (e) => {
  if (!e.valid) {
    console.error('Error adding medical history: ', e.errors)
    return
  }

  addMedicalHistory(e.values)
}
</script>
