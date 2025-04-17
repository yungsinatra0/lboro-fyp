<template>
  <Dialog
    v-model:visible="displayAddDialog"
    modal
    header="Adauga o înregistrare medicală"
    class="w-[95vw] md:w-1/2"
    @hide="emit('close')"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-2">
        <span class="font-bold text-xl md:text-2xl">Înregistrare medicală nouă</span>
      </div>
    </template>
    <div v-if="!loadingState && !extractionResult">
      <span class="text-surface-500 dark:text-surface-400 block mb-2"
        >Adaugă informații pentru o nouă înregistrare medicală.</span
      >
      <div class="text-rose-600 text-sm mb-2 md:mb-4">* Câmpurile marcate sunt obligatorii</div>
      <span v-if="formError" class="text-rose-600 text-sm block mb-4 md:mb-8">{{ formError }}</span>
      <Form
        v-slot="$form"
        :initialValues="initialValues"
        @submit="onFormSubmit"
        :resolver="resolver"
      >
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
          <label for="name" class="font-semibold w-full md:w-24"
            >Descriere <span class="text-rose-600">*</span></label
          >
          <div class="w-full md:w-1/2">
            <InputText name="name" class="w-full" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.name?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.name.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
          <label for="doctor_name" class="font-semibold w-full md:w-24"
            >Numele doctorului <span class="text-rose-600">*</span></label
          >
          <div class="w-full md:w-1/2">
            <InputText name="doctor_name" class="w-full" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.doctor_name?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.doctor_name.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
          <label for="place" class="font-semibold w-full md:w-24">Locație</label>
          <div class="w-full md:w-1/2">
            <InputText name="place" class="w-full" autocomplete="off" type="text" fluid />
            <Message
              v-if="$form.place?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.place.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
          <label for="category" class="font-semibold w-full md:w-24"
            >Categorie <span class="text-rose-600">*</span></label
          >
          <div class="w-full md:w-1/2">
            <Select
              name="category"
              :options="categories"
              placeholder="Selectează categoria"
              class="w-full"
              fluid
            />
            <Message
              v-if="$form.category?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.category.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4" v-if="$form.category?.value === 'Consultație'">
          <label for="subcategory" class="font-semibold w-full md:w-24">Subcategorie consultație</label>
          <div class="w-full md:w-1/2">
            <Select
              name="subcategory"
              :options="subcategories"
              placeholder="Selectează subcategoria"
              class="w-full"
              fluid
            />
            <Message
              v-if="$form.subcategory?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.subcategory.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4" v-if="$form.category?.value === 'Laborator'">
          <label for="labsubcategory" class="font-semibold w-full md:w-24">Subcategorie laborator</label>
          <div class="w-full md:w-1/2">
            <Select
              name="labsubcategory"
              :options="labsubcategories"
              placeholder="Selectează subcategoria"
              class="w-full"
              fluid
            />
            <Message
              v-if="$form.labsubcategory?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.labsubcategory.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4" v-if="$form.category?.value === 'Laborator'">
          <label for="extract" class="font-semibold w-full md:w-24">Extrage date laborator cu AI?</label>
          <ToggleSwitch name="extract" />
          <Message
            v-if="$form.extract?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm mt-1"
            >{{ $form.extract.error.message }}</Message
          >
        </div>
        
        <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
          <label for="date_consultation" class="font-semibold w-full md:w-24"
            >Data efectuării<span class="text-rose-600">*</span></label
          >
          <div class="w-full md:w-1/2">
            <DatePicker
              name="date_consultation"
              dateFormat="dd/mm/yy"
              placeholder="Data"
              showIcon
              fluid
              class="w-full"
              :maxDate="maxDate"
            />
            <Message
              v-if="$form.date_consultation?.invalid"
              severity="error"
              size="small"
              variant="simple"
              class="text-rose-600 text-sm mt-1"
              >{{ $form.date_consultation.error.message }}</Message
            >
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row gap-2 md:gap-4 mb-4">
          <label for="notes" class="font-semibold w-full md:w-24">Notite</label>
          <Textarea
            name="notes"
            class="w-full md:w-1/2"
            autocomplete="off"
            type="text"
            fluid
            rows="3"
            placeholder="Adaugă note sau observații"
          />
        </div>
        
        <div class="my-4">
          <FileUpload
            name="file"
            mode="basic"
            @select="onSelect"
            :multiple="false"
            :custom-upload="true"
            :maxFileSize="10000000"
            choose-label="Adauga documentul medical"
            class="w-full md:w-1/3"
          >
          </FileUpload>
        </div>
        
        <div class="shrink-0 pt-3 flex justify-end gap-2">
          <Button
            label="Anulează"
            outlined
            severity="danger"
            @click="emit('close')"
            autofocus
            type="button"
            class="text-sm md:text-base px-2 md:px-4"
          />
          <Button 
            label="Salvează" 
            severity="success" 
            autofocus 
            type="submit" 
            class="text-sm md:text-base px-2 md:px-4"
          />
        </div>
      </Form>
    </div>
    <div v-else>
      <div class="flex flex-col items-center p-4" v-if="!extractionResult">
        <ProgressSpinner />
        <p class="mt-3">Se procesează documentul...</p>
      </div>

      <div v-else class="flex flex-col items-center p-4">
        <div v-if="!extractSuccess" class="w-full">
          <h2 class="text-lg md:text-xl font-medium mb-4">Analizati rezultatele extrase si schimbati daca sunt gresite</h2>
          
          <div class="mb-4">
            <IconField class="w-full">
              <InputIcon>
                <i class="pi pi-search" />
              </InputIcon>
              <InputText
                class="w-full"
                size="small"
                v-model="filters['global'].value"
                placeholder="Cauta..."
              />
            </IconField>
          </div>

          <div class="w-full overflow-x-auto">
            <DataTable
              :value="extractionResult"
              v-model:editingRows="editingRows"
              class="w-full"
              :rows="5"
              :rowsPerPageOptions="[5, 10, 20]"
              editMode="row"
              paginator
              paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
              currentPageReportTemplate="{first}-{last}"
              dataKey="test_name"
              @row-edit-save="onRowEditSave"
              v-model:filters="filters"
              :globalFilterFields="['test_name', 'test_code']"
              breakpoint="0px"
              scrollable
              scrollHeight="flex"
            >
              <Column v-for="col of columns" :key="col.field" :field="col.field" :header="col.header">
                <template #editor="{ data, field }">
                  <InputText v-model="data[field]" class="w-full" fluid />
                </template>
                <template #body="{ data, field }">
                  <span v-if="field != 'test_name'" class="block truncate max-w-[120px] text-sm md:text-base md:max-w-none">{{ data[field] }}</span>
                  <span v-else class="font-semibold text-sm">{{ data[field] }}</span>
                </template>
              </Column>
              <Column
                :rowEditor="true"
                style="width: 10%; min-width: 6rem"
                bodyStyle="text-align:center"
              />
            </DataTable>
          </div>
          
          <div class="shrink-0 pt-3 flex justify-end gap-2">
            <Button
              label="Salvează"
              severity="success"
              @click="addExtractedLab()"
              autofocus
              type="button"
              class="text-sm md:text-base px-3 py-2 md:px-4"
            />
            <Button
              label="Anulează"
              outlined
              severity="danger"
              @click="emit('close')"
              autofocus
              type="button"
              class="text-sm md:text-base px-3 py-2 md:px-4"
            />
          </div>
        </div>
        <div v-else class="flex flex-col items-center p-4 md:p-8">
          <i class="pi pi-check-circle text-4xl md:text-6xl text-green-500 mb-4" />
          <Message severity="success" class="mb-6 text-base md:text-lg">
            Rezultatele au fost extrase cu succes! Acestea sunt acum disponibile in sectiunea de
            laborator.
          </Message>
          <Button
            label="Vezi rezultatele"
            severity="success"
            class="px-4 py-2 md:px-6 md:py-3 text-base md:text-lg"
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
import { FilterMatchMode } from '@primevue/core/api'
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

  // if filtering, get original index
  // if not filtering, can just edit the data directly
  // need to compare test name and something else like method or unit to find the original index

  if (filters.value.global.value) {
    const originalIndex = extractionResult.value.findIndex((item) => item.test_name === newData.test_name && item.method === newData.method && item.unit === newData.unit)
    index = originalIndex
  }
  
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